from django.db import models
from django.urls import reverse


class Category(models.Model):
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, db_index=True, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("main:product_list_by_category", args=[self.slug])

class Subcategory_1(models.Model):
    category = models.ForeignKey(Category, related_name='subcategory_1', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, db_index=True, unique=True)

    class Meta:
        ordering = ['name', 'category']
        verbose_name = 'Подкатегория_1'
        verbose_name_plural = 'Подкатегории_1'
    
    def __str__(self):
        return f'{self.name} >> {self.category}'
    
    def get_absolute_url(self):
        return reverse("main:product_list_by_subcategory", args=[self.slug])

class Subcategory_2(models.Model):
    category_main = models.ForeignKey(Category, related_name='subcategory_2', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory_1, related_name='parent_subcategory', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, db_index=True, unique=True)

    class Meta:
        ordering = ['name', 'category_main', 'subcategory']
        verbose_name = 'Подкатегория_2'
        verbose_name_plural = 'Подкатегории_2'
    
    def __str__(self):
        return f'{self.name} >> {self.subcategory} >> {self.category_main}'
    
    def get_absolute_url(self):
        return reverse("main:product_list_by_subcategory_sub", args=[self.slug])
    
    
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    subcategory_1 = models.ForeignKey(Subcategory_1, related_name='product_sub', on_delete=models.CASCADE, blank=True, null=True)
    subcategory_2 = models.ForeignKey(Subcategory_2, related_name='product_sub_cat', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=400, db_index=True, unique=True)
    description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name', '-price', 'available', 'available_quantity']
    
    def __str__(self):
        return f'{self.name} >> {self.category}'
    
    def get_absolute_url(self):
        return reverse("detail_product", args=[self.slug])
    
class Specifications(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Характеристики'
        verbose_name_plural = 'Характеристики'

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification = models.ForeignKey(Specifications, on_delete=models.CASCADE)
    value = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Характеристики Товара'
        verbose_name_plural = 'Характеристики Товара'

class Galery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False) # Флаг для главного изображения

    class Meta:
        ordering = ['-is_main']
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображение товаров'


    def __str__(self):
        return f'Image of product >> {self.product.name}'