from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Subcategory_1, Favorite
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CategorySerializer, ProductSerializer, SubcategorySerializer
from rest_framework import status
import pandas as pd
from django.core.files.storage import default_storage
from django.core.files import File
import os
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.text import slugify
from django.conf import settings
import unidecode

def search_result(request):
    query = request.GET.get('q', '')

    if not query:
        return render(request, 'main/products/search_results.html', {'query':query, 'results':[]})
    
    categories = Category.objects.filter(name__icontains=query)
    subcategories = Subcategory_1.objects.filter(name__icontains=query)

    products_by_name = Product.objects.filter(name__icontains=query)

    products_by_category = Product.objects.filter(category__in=categories)
    products_by_subcategory = Product.objects.filter(subcategory_1__in=subcategories)

    results = products_by_name | products_by_category | products_by_subcategory

    return render(request, 'main/products/search_results.html', {'query':query, 'results':results.distinct()})


def about_us(request):
    return render(request, 'main/index/about_us.html')

def guarentee(request):
    return render(request, 'main/index/guarentee.html')

def contacts(request):
    return render(request, 'main/index/contacts.html')

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
    products = Product.objects.filter(category=category)

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
    products = Product.objects.filter(subcategory_1=sub_category_1)

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
    product = get_object_or_404(Product, slug=slug)
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


def parse_speficiations(value):
    if isinstance(value, str):
        specs = {}
        pairs = value.split(",")
        for pair in pairs:
            if ':' in pair:
                key, val = pair.split(":", 1)
                specs[key.strip()] = val.strip()
        return specs
    return value if isinstance(value, dict) else {}

def custom_slugify(value):
    return slugify(unidecode.unidecode(value))

def save_image_from_path(image_path, product, image_field):
    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as img_file:
            file_name = os.path.basename(image_path)
            getattr(product, image_field).save(file_name, File(img_file), save=True)



@staff_member_required
def upload_products(request):
    print("Функция upload_products вызвана")

    if request.method == 'POST':
        print("POST-запрос получен")
        
        if 'file' not in request.FILES:
            messages.error(request, 'Файл не был загружен')
            return redirect('main:upload_products')

        file = request.FILES['file']
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension not in ['csv', 'xlsx']:
            messages.error(request, 'Формат файла должен быть CSV или XLSX')
            return redirect('main:upload_products')

        
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)  
        file_path = os.path.join(upload_dir, file.name)

        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        print(f"Файл сохранен: {file_path}")

        try:
            
            if file_extension == 'csv':
                df = pd.read_csv(file_path, encoding='utf-8', dtype=str)
            else:
                df = pd.read_excel(file_path, engine='openpyxl', dtype=str)

            print("Содержимое файла:\n", df.head())

            
            required_columns = {'Категория', 'Подкатегория', 'Название', 'Описание', 'Цена', 'В наличии', 'Количество'}
            if not required_columns.issubset(df.columns):
                messages.error(request, 'Ошибка: В файле отсутствуют необходимые колонки.')
                return redirect('main:upload_products')

            
            for _, row in df.iterrows():
                try:
                    category_name = row['Категория'].strip()
                    subcategory_name = row['Подкатегория'].strip()
                    product_name = row['Название'].strip()

                    
                    category_slug = custom_slugify(category_name)
                    subcategory_slug = custom_slugify(subcategory_name)
                    product_slug = custom_slugify(product_name)
                    category, _ = Category.objects.get_or_create(name=category_name, defaults={'slug': category_slug})

                    specifications = parse_speficiations(row.get('Характеристики', ''))
                    complectation = parse_speficiations(row.get('Комлектация', ''))

                    
                    
                    subcategory, _ = Subcategory_1.objects.get_or_create(
                        name=subcategory_name, 
                        category=category, 
                        defaults={'slug': subcategory_slug}
                    )

                    product, created = Product.objects.get_or_create(
                        name=product_name,
                        slug=product_slug,
                        category=category,
                        subcategory_1=subcategory,
                        defaults={
                            'description': row['Описание'],
                            'price': float(row['Цена']),
                            'available': row['В наличии'].strip().lower() in ['true', 'да', 'yes', '1'],
                            'available_quantity': int(row['Количество']),
                            'specifications': specifications,
                            'complectation': complectation,
                        }
                    )

                    image_columns = {"Изображение 1": "image_1", "Изображение 2": "image_2", "Изображение 3": "image_3"}
                    for col_name, field_name in image_columns.items():
                        if col_name in df.columns:
                            image_path = row[col_name].strip()
                            save_image_from_path(image_path, product, field_name)
                            


                    if created:
                        print(f"Товар создан: {product_name}")
                    else:
                        print(f"Товар обновлен: {product_name}")

                except Exception as row_error:
                    print(f"Ошибка в строке: {row} -> {row_error}")

            messages.success(request, 'Товары успешно загружены!')
        except Exception as e:
            messages.error(request, f'Ошибка при обработке файла: {e}')
        finally:
            os.remove(file_path)  
            print(f"Файл удален: {file_path}")

        return redirect('main:upload_products')

    return render(request, 'main/products/upload_products.html')


