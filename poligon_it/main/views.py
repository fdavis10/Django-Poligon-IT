from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Subcategory_1, Subcategory_2, ProductSpecification


def navigation(request):
    categories = Category.objects.prefetch_related('subcategory_1', 'subcategory_1__parent_subcategory').all()
    return render(request, 'base.html', {
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
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    return render(request, 'main/products/category_list.html', {
        'category': category,
        'products': products
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
    
    # add cart add form

    return render(request, 'main/products/detail_product.html', {
        'product': product
    })
    