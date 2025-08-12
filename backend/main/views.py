from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Subcategory_1, Favorite
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CategorySerializer, ProductSerializer, SubcategorySerializer
from rest_framework import status
import pandas as pd
from django.core.files import File
import os
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.text import slugify
from django.conf import settings
import unidecode
import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import mimetypes
from urllib.request import urlopen
from django.core.files.temp import NamedTemporaryFile
from django.utils.crypto import get_random_string
import tempfile
import zipfile
from django.http import HttpResponse


YANDEX_API_TOKEN = os.getenv('YANDEX_API_TOKEN')



def search_result(request):
    query = request.GET.get('q', '')

    if not query:
        return render(request, 'main/products/search_results.html', {'query':query, 'results':[]})
    
    categories = Category.objects.filter(name__icontains=query)
    subcategories = Subcategory_1.objects.filter(name__icontains=query)

    products_by_name = Product.objects.filter(name__icontains=query)

    products_by_category = Product.objects.filter(category__in=categories)
    products_by_subcategory = Product.objects.filter(subcategory_1__in=subcategories)

    products_by_pk = Product.objects.none()
    if query.isdigit():
        products_by_pk = Product.objects.filter(pk=query)

    results = products_by_name | products_by_category | products_by_subcategory | products_by_pk

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
    return redirect('main:favorite_list')

def remove_from_favorites(request, product_id):
    session_key = get_session_key(request)
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.filter(session_key=session_key, product=product).delete()
    return redirect('main:favorite_list')

def clear_favorites(request):
    if 'favorites' in request.session:
        del request.session['favorites']
        request.session.modified = True
    return redirect('main:favorite_list')

def favorites_list(request):
    session_key = get_session_key(request)
    favorites = Product.objects.filter(favorite__session_key=session_key)
    return render(request, 'main/products/favorites.html', {'favorites':favorites})

def index_page(request):
    session_key = get_session_key(request)
    execluded_slugs = ['sredstvo-protivodeistviia-bpla']
    products = Product.objects.exclude(category__slug__in=execluded_slugs)[:8]
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
            subquery = Q()
            for value in selected_values:
                subquery |= Q(specifications__contains={key: value})
            query &= subquery 

    if query:
        products = products.filter(query)

    products_exist = products.exists()

    return render(request, 'main/products/category_list.html', {
        'category': category,
        'products': products,
        'filters': filters,
        'categories': categories,
        'products_exist': products_exist,
    })

def product_list_by_subcategory(request, category_slug, subcategory_slug):
    category = get_object_or_404(Category, slug=category_slug)
    subcategory = get_object_or_404(Subcategory_1, slug=subcategory_slug, category=category)
    products = Product.objects.filter(subcategory_1=subcategory)

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
        'subcategory': subcategory,
        'products': products,
        'filters': filters,
    })

def detail_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    categories = Category.objects.all()
    subcategories = Subcategory_1.objects.all()
    return render(request, 'main/products/detail_product.html', {
        'product': product,
        'categories': categories,
        'subcategories': subcategories, 
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


# def download_yandex_file(yandex_url):
#     api_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download'
#     params = {'public_key': yandex_url}
#     headers = {'Authorization': f'OAuth {YANDEX_API_TOKEN}'}
#     response = requests.get(api_url, headers=headers, params=params)
#     response.raise_for_status()
#     download_url = response.json()['href']
#     return download_url

# def download_and_save_image(product, field_name, url, slug):
#     try:
#         print(f"Trying to download: {url}")
#         response = requests.get(url)
#         if response.status_code == 200:
#             ext = mimetypes.guess_extension(response.headers.get("Content-Type", "image/jpeg"))
#             if not ext:
#                 ext = ".jpg"
#             filename = f"{slug}_{get_random_string(8)}{ext}"
            
#             # Windows fix: use NamedTemporaryFile without delete
#             temp_file = tempfile.NamedTemporaryFile()
#             temp_file.write(response.content)
#             temp_file.flush()
#             return File(temp_file, name=filename)
#         else:
#             print(f"Error: Image not accessible. Status code: {response.status_code}")
#     except Exception as e:
#         print(f"Error! Failed to save image from {url}: {e}")
#     return None


# SAVE IMAGE FROM PATH OLDES [06.04.2025]

# def save_image_from_path(image_path, product, image_field):
#     try:
#         if image_path.startswith('http://') or image_path.startswith('https://'):
#             response = requests.get(image_path, timeout=10)
#             if response.status_code == 200:
#                 file_name = os.path.basename(image_path)
#                 conen(image_path, 'rb') as img_file:
#                 file_name = os.path.basename(image_path)
#                 getattr(product, image_field).save(file_name, File(img_file), save=True)
#     except Exception as e:
#         print(f'Error in save {image_path}: {e}')

# @staff_member_required
# def upload_products(request):
#     print("Функция upload_products вызвана")

#     if request.method == 'POST':
#         print("POST-запрос получен")
        
#         if 'file' not in request.FILES:
#             messages.error(request, 'Файл не был загружен')
#             return redirect('main:upload_products')

#         file = request.FILES['file']
#         file_extension = file.name.split('.')[-1].lower()
        
#         if file_extension not in ['csv', 'xlsx']:
#             messages.error(request, 'Формат файла должен быть CSV или XLSX')
#             return redirect('main:upload_products')

        
#         upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
#         os.makedirs(upload_dir, exist_ok=True)  
#         file_path = os.path.join(upload_dir, file.name)

        
#         with open(file_path, 'wb+') as destination:
#             for chunk in file.chunks():
#                 destination.write(chunk)
#         print(f"Файл сохранен: {file_path}")

#         try:
            
#             if file_extension == 'csv':
#                 df = pd.read_csv(file_path, encoding='utf-8', dtype=str)
#             else:
#                 df = pd.read_excel(file_path, engine='openpyxl', dtype=str)

#             print("Содержимое файла:\n", df.head())

            
#             required_columns = {'Категория', 'Подкатегория', 'Название', 'Описание', 'Цена', 'В наличии', 'Количество'}
#             if not required_columns.issubset(df.columns):
#                 messages.error(request, 'Ошибка: В файле отсутствуют необходимые колонки.')
#                 return redirect('main:upload_products')

            
#             AVAILABILITY_MAP = {
#                 'В наличии': 'in_stock',
#                 'Под заказ': 'by_order',
#                 'Нет в наличии': 'out_of_stock',
#                 'Нет': 'out_of_stock',
#                 'Да':'in_stock',
#                 '0': 'out_of_stock',
#                 '1': 'in_stock',
#                 'by_order': 'by_order',
#                 'in_stock': 'in_stock',
#                 'out_of_stock': 'out_of_stock',
#             }
            
            
#             df.columns = df.columns.str.strip().str.lower()


#             for _, row in df.iterrows():
#                 try:
#                     category_name = row['категория'].strip()
#                     subcategory_name = row['подкатегория'].strip()
#                     product_name = row['название'].strip()

                    
#                     category_slug = custom_slugify(category_name)
#                     subcategory_slug = custom_slugify(subcategory_name)
#                     product_slug = custom_slugify(product_name)
#                     category, _ = Category.objects.get_or_create(name=category_name, defaults={'slug': category_slug})

#                     specifications = parse_speficiations(row.get('характеристики', ''))
#                     complectation = row.get('комплектация', '').strip()

                    
                    
#                     subcategory, _ = Subcategory_1.objects.get_or_create(
#                         name=subcategory_name, 
#                         category=category, 
#                         defaults={'slug': subcategory_slug}
#                     )

#                     product, created = Product.objects.get_or_create(
#                         name=product_name,
#                         slug=product_slug,
#                         category=category,
#                         subcategory_1=subcategory,
#                         defaults={
#                             'description': row['описание'],
#                             'price': float(row['цена']),
#                             'available': AVAILABILITY_MAP.get(row['в наличии'].strip().lower(), 'in_stock'),
#                             'available_quantity': int(row['количество']),
#                             'specifications': specifications,
#                             'complectation': complectation,
#                         }
#                     )

#                     # image_columns = {"Изображение 1": "image_1", "Изображение 2": "image_2", "Изображение 3": "image_3"}
#                     # for col_name, field_name in image_columns.items():
#                     #     if col_name in df.columns:
#                     #         image_url = row[col_name].strip()
#                     #         full_url = f'https://getfile.dokpub.com/yandex/get/{image_url}'
#                     #         download_and_save_image(product, field_name, full_url, product_slug)
                            

                    
#                     product.description = row['описание']
#                     product.price = float(row['цена'])
#                     product.available = AVAILABILITY_MAP.get(row['в наличии'].strip().lower(), 'in_stock')
#                     product.available_quantity = int(row['количество'])
#                     product.specifications = specifications
#                     product.complectation = complectation
#                     product.save()


#                     if created:
#                         print(f"Товар создан: {product_name}")
#                     else:
#                         print(f"Товар обновлен: {product_name}")

#                 except Exception as row_error:
#                     print(f"Ошибка в строке: {row} -> {row_error}")

#             messages.success(request, 'Товары успешно загружены!')
#         except Exception as e:
#             messages.error(request, f'Ошибка при обработке файла: {e}')
#         finally:
#             os.remove(file_path)  
#             print(f"Файл удален: {file_path}")

#         return redirect('main:upload_products')

#     return render(request, 'main/products/upload_products.html')

@staff_member_required
def upload_products(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
            df.columns = df.columns.str.strip().str.lower()

            AVAILABILITY_MAP = {
                'в наличии': 'in_stock',
                'под заказ': 'by_order',
                'нет в наличии': 'out_of_stock',
                'нет': 'out_of_stock',
                '0': 'out_of_stock',
                'да': 'in_stock',
                '1': 'in_stock',
                'by_order': 'by_order',
                'in_stock': 'in_stock',
                'out_of_stock': 'out_of_stock',
            }

            for _, row in df.iterrows():
                try:
                    category_name = row['категория'].strip()
                    subcategory_name = row['подкатегория'].strip()
                    product_name = row['название'].strip()
                    description = row['описание']
                    price_raw = str(row['цена']).strip().lower()
                    quantity = int(row['количество'])

                    if price_raw in ['по запросу', 'по запросу.']:
                        price = None
                        price_on_request = True
                    else:
                        price = float(price_raw.replace(',', '.'))
                        price_on_request = False


                    availability_raw = str(row.get('в наличии', '')).strip().lower()
                    available = AVAILABILITY_MAP.get(availability_raw, 'in_stock')
                    category_slug = custom_slugify(category_name)
                    subcategory_slug = custom_slugify(subcategory_name)
                    product_slug = custom_slugify(product_name)

                    category, _ = Category.objects.get_or_create(
                        name=category_name,
                        defaults={'slug': category_slug}
                    )

                    subcategory, _ = Subcategory_1.objects.get_or_create(
                        name=subcategory_name,
                        category=category,
                        defaults={'slug': subcategory_slug}
                    )

                    specifications = parse_speficiations(row.get('характеристики', ''))
                    complectation = row.get('комплектация', '').strip()

                    product, _ = Product.objects.update_or_create(
                        name=product_name,
                        slug=product_slug,
                        category=category,
                        subcategory_1=subcategory,
                        defaults={
                            'description': description,
                            'price': price,
                            'price_on_request': price_on_request,
                            'available': available,
                            'available_quantity': quantity,
                            'specifications': specifications,
                            'complectation': complectation,
                        }
                    )

                except Exception as e:
                    print(f"Ошибка в строке:\n{row}\n-> {e}")

            return redirect('main:index_page')

        except Exception as e:
            print(f"Ошибка обработки файла: {e}")

    return render(request, 'main/products/upload_products.html')


def download_all_docs(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    files_to_zip = []

    if product.certificate_diller:
        files_to_zip.append(product.certificate_diller.path)
    if product.certificate_two:
        files_to_zip.append(product.certificate_two.path)
    if product.certificate_tree:
        files_to_zip.append(product.certificate_tree.path)
    if product.guarantee:
        files_to_zip.append(product.guarantee.path)
    
    zip_filename = os.path.join(temp_dir, f'{product.name}_documents.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file_path in files_to_zip:
            zipf.write(file_path, os.path.basename(file_path))
    
    with open(zip_filename, 'rb') as zipf:
        response = HttpResponse(zipf.read(), content_type ='application/zip')
        response['Content-Disposition'] = f'attachment; filname={os.path.basename(zip_filename)}'
        return response