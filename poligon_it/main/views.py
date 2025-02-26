from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Subcategory_1, Subcategory_2
from django.db.models import Q


def navigation(request):
    categories = Category.objects.prefetch_related('subcategory_1', 'subcategory_1__parent_subcategory').all()
    return render(request, 'base.html', {
        'categories': categories
    })

def about_us(request):
    categories = Category.objects.prefetch_related('subcategory_1', 'subcategory_1__parent_subcategory').all()
    return render(request, 'main/index/about_us.html',
                  {
                      'categories': categories
                  })


def index_page(request):
    categories = Category.objects.all()
    products = Product.objects.all()[:8]
    return render(request, 'main/index/index.html', {
        'products': products,
        'categories': categories
        })

def product_list_by_category(request, slug):
    categories = Category.objects.prefetch_related('subcategory_1', 'subcategory_1__parent_subcategory').all()
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
    return render(request, 'main/products/sub_category_list.html', {
        'subcategory': sub_category_1,
        'products': products
    })

def product_list_by_sub_subcategory(request, slug):
    subcategory_2 = get_object_or_404(Subcategory_2, slug=slug)
    products = Product.objects.filter(subcategory_2=subcategory_2)
    if products.exists():
        return render(request, 'main/products/product_list_by_sub_subcategory.html', {
            'subcategory_2': subcategory_2,
            'products': products
        })
    else:
        parent_category = subcategory_2.category_main
        parent_subcategory = subcategory_2.subcategory
        return render(request, 'main/products/sub_subcategory_empty.html', {
            'subcategory': subcategory_2,
            'parent_category': parent_category,
            'parent_subcategory': parent_subcategory
        })

def detail_product(request, slug):
    product = get_object_or_404(Product, slug=slug, available = True)
    categories = Category.objects.prefetch_related('subcategory_1', 'subcategory_1__parent_subcategory').all()
    
    # add cart add form

    return render(request, 'main/products/detail_product.html', {
        'product': product,
        'categories': categories
    })
    