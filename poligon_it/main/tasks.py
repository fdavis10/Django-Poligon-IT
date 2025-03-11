import requests
from django.conf import settings
from main.models import Product, Category
from celery import shared_task
from django.shortcuts import get_object_or_404


ONE_C_URL = "" # http://ip_server_1С/odata/standard.odata/Catalog_Номенклатура
ONE_C_USER = "" # login
ONE_C_PASSWORD = "" # password

def import_product_from_1c():
    response = requests.get(ONE_C_URL, auth=(ONE_C_USER, ONE_C_PASSWORD))

    if response.status_code == 200:
        data = response.json()['value']

        for item in data:
            category_name = item.get("Категория", "Без категории")
            category, _ = Category.objects.get_or_create(name=category_name, defaults={"slug": category_name.lower().replace(" ","-")})
            product, created = Product.objects.update_or_create(
                slug=item['Ref_Key'],
                defaults = {
                    "name": item["Description"],
                    "price": item.get("Цена", 0),
                    "description": item.get(("Описание", "")),
                    "available_quantity": item.get("Остаток", 0),
                    "available": item.get("Остаток", 0) > 0,
                    "image_1": item.get("Картинка", ""),
                    "category":category,
                }
            )
            print(f"{'Добавлен' if created else 'Обновлен'}: {product.name}")
    else:
        print("Ошибка подключения к 1C: ", response.status_code)
        
