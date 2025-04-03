import requests
from django.conf import settings
from main.models import Product, Category, Subcategory_1
from celery import shared_task
from django.shortcuts import get_object_or_404
import logging
import os
from django.utils.text import slugify



ONE_C_PRODUCTS_URL = os.getenv("ONE_C_PRODUCTS_URL")
ONE_C_USER = os.getenv("ONE_C_USER")
ONE_C_PASSWORD = os.getenv("ONE_C_PASSWORD")


def generate_unique_slug(model, name, default="unknows"):
    base_slug = slugify(name) or default
    unique_slug = base_slug
    count = 1

    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{count}"
        count += 1

    return unique_slug


@shared_task
def fetch_products_from_1c():
    if not ONE_C_PRODUCTS_URL:
        logging.error("Не указан URL API 1C в .env")
        return

    try:
        response = requests.get(ONE_C_PRODUCTS_URL, auth=(ONE_C_USER, ONE_C_PASSWORD), timeout=10)
        response.raise_for_status()
        data = response.json().get('products', [])
        
        for item in data:
            category_name = item.get("category", "Без категории").strip()
            category_slug = generate_unique_slug(Category, category_name, "unknown-category")
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={"slug": category_slug}
            )

            subcategory_name = item.get("subcategory_1", "").strip()
            subcategory_slug = generate_unique_slug(Subcategory_1, subcategory_name, "unknown-subcategory")
            subcategory, _ = Subcategory_1.objects.get_or_create(
                name=subcategory_name,
                category=category,
                defaults={"slug": subcategory_slug}
            )

            product_slug = generate_unique_slug(Product, item.get('name', "unknown-product"))
            product, created = Product.objects.get_or_create(
                slug=product_slug,
                defaults={
                    "name": item["name"],
                    "description": item.get("description", ""),
                    "price": item.get("price", 0),
                    "available_quantity": item.get("stock", 0),
                    "available": item.get("stock", 0) > 0,
                    "image_1": item.get("image_1", ""),
                    "image_2": item.get("image_2", ""),
                    "image_3": item.get("image_3", ""),
                    "specifications": item.get("specifications", {}),
                    "complectation": item.get("complectation", {}),
                    "category": category,
                    "subcategory_1": subcategory
                }
            )

            logging.info(f"{'Добавлен' if created else 'Обновлен'} товар: {product.name}")

    except requests.RequestException as e: 
        logging.error(f"Ошибка при запросе к 1С: {e}")
