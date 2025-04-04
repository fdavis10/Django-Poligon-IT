# Generated by Django 5.1.7 on 2025-04-02 17:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='category_images/')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('slug', models.SlugField(max_length=300, unique=True)),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ['name'],
                'indexes': [models.Index(fields=['name'], name='main_catego_name_5111b9_idx')],
            },
        ),
        migrations.CreateModel(
            name='Subcategory_1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('slug', models.SlugField(max_length=300, unique=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategory_1', to='main.category')),
            ],
            options={
                'verbose_name': 'Подкатегория_1',
                'verbose_name_plural': 'Подкатегории_1',
                'ordering': ['name', 'category'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_1', models.ImageField(default='default.webp', upload_to='product/')),
                ('image_2', models.ImageField(blank=True, default='default.webp', upload_to='product/')),
                ('image_3', models.ImageField(blank=True, default='default.webp', upload_to='product/')),
                ('video', models.FileField(blank=True, null=True, upload_to='product/videos/', verbose_name='Видео товара')),
                ('name', models.CharField(db_index=True, max_length=300)),
                ('slug', models.SlugField(max_length=400, unique=True)),
                ('description', models.TextField(max_length=500)),
                ('specifications', models.JSONField(blank=True, default=dict, verbose_name='Технические характеристики')),
                ('complectation', models.JSONField(blank=True, default=dict, verbose_name='Комлектация товара')),
                ('certificate_diller', models.FileField(blank=True, null=True, upload_to='certificates/', verbose_name='Сертификат диллера')),
                ('guarantee', models.FileField(blank=True, null=True, upload_to='guaranties/', verbose_name='Гарантия товара')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('available', models.BooleanField(default=True)),
                ('available_quantity', models.DecimalField(decimal_places=1, default=0, max_digits=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='main.category')),
                ('subcategory_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_sub', to='main.subcategory_1')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
                'ordering': ['name', '-price', 'available', 'available_quantity'],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(db_index=True, max_length=1024)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.product')),
            ],
            options={
                'unique_together': {('session_key', 'product')},
            },
        ),
    ]
