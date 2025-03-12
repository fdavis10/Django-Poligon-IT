from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Subcategory_1, Favorite
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CategorySerializer, ProductSerializer, SubcategorySerializer
from rest_framework import status

def search_result(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'main/products/search_results.html', {'query':query, 'results': results})


def about_us(request):
    return render(request, 'main/index/about_us.html')

def get_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def add_to_favorites(request, product_id):
    session_key = get_session_key(request)
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.get_or_create(session_key=session_key, product=product)
    return redirect('main:index_page')

def remove_from_favorites(request, product_id):
    session_key = get_session_key(request)
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.filter(session_key=session_key, product=product).delete()
    return redirect('main:index_page')

def clear_favorites(request):
    if 'favorites' in request.session:
        del request.session['favorites']
        request.session.modified = True
    return redirect('main:index_page')

def favorites_list(request):
    session_key = get_session_key(request)
    favorites = Product.objects.filter(favorite__session_key=session_key)
    return render(request, 'main/products/favorites.html', {'favorites':favorites})

def index_page(request):
    session_key = get_session_key(request)
    products = Product.objects.all()[:8]
    return render(request, 'main/index/index.html', {
        'products': products,
        })

def product_list_by_category(request, slug):
    categories = Category.objects.prefetch_related('subcategory_1').all()
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)

    filters = {}
    for product in products:
        if isinstance(product.specifications, dict):
            for key, value in product.specifications.items():
                if key not in filters:
                    filters[key] = set()
                filters[key].add(str(value))
    filters = {key: list(values) for key, values in filters.items()}

    print('Параметры запроса:', request.GET)

    query = Q()
    for key in filters.keys():
        selected_values = request.GET.getlist(key)
        if selected_values:
            for value in selected_values:
                query |= Q(specifications__contains={key: value})

    if query:
        products = products.filter(query)

    return render(request, 'main/products/category_list.html', {
        'category': category,
        'products': products,
        'filters': filters,
        'categories': categories,
    })

def product_list_by_subcategory(request, slug):
    sub_category_1 = get_object_or_404(Subcategory_1, slug=slug)
    products = Product.objects.filter(subcategory_1 = sub_category_1)

    filters = {}
    for product in products:
        if isinstance(product.specifications, dict):
            for key, value in product.specifications.items():
                if key not in filters:
                    filters[key] = set()
                filters[key].add(str(value))
    filters = {key: list(values) for key, values in filters.items()}

    query = Q()
    for key in filters.keys():
        selected_values = request.GET.getlist(key)
        if selected_values:
            for value in selected_values:
                query |= Q(specifications__contains={key: value})

    if query:
        products = products.filter(query)

    return render(request, 'main/products/product_list_by_subcategory.html', {
        'subcategory': sub_category_1,
        'products': products,
        'filters': filters,
    })

def detail_product(request, slug):
    product = get_object_or_404(Product, slug=slug, available = True)
    return render(request, 'main/products/detail_product.html', {
        'product': product, 
    })

def mobile_search(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'main/products/mobile_search.html', {'query':query, 'results': results})


@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_subcategories(request):
    subcategories = Subcategory_1.objects.all()
    serializer = SubcategorySerializer(subcategories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


