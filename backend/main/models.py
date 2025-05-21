from django.db import models
from django.urls import reverse
from .utils import compress_image


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
    slug = models.SlugField(max_length=300, db_index=True)

    class Meta:
        ordering = ['name', 'category']
        verbose_name = 'Подкатегория_1'
        verbose_name_plural = 'Подкатегории_1'
    
    def __str__(self):
        return f'{self.name} >> {self.category}'
    
    def get_absolute_url(self):
        return reverse("main:product_list_by_subcategory", args=[self.category.slug, self.slug])
    
    
class Product(models.Model):

    class AvailabilityChoices(models.TextChoices):
        IN_STOCK = 'in_stock', 'В наличии'
        OUT_OF_STOCK = 'out_of_stock', 'Нет в наличии'
        BY_ORDER = 'by_order', 'Под заказ'


    image_1 = models.ImageField(upload_to='product/', blank=False, null=False, default='default.webp')
    image_2 = models.ImageField(upload_to='product/', blank=True, default='default.webp')
    image_3 = models.ImageField(upload_to='product/', blank=True, default='default.webp')
    video = models.FileField(upload_to='product/videos/', blank=True, null=True, verbose_name='Видео товара')
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    subcategory_1 = models.ForeignKey(Subcategory_1, related_name='product_sub', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=400, db_index=True, unique=True)
    description = models.TextField(max_length=500)
    specifications = models.JSONField(default=dict, blank=True, verbose_name='Технические характеристики')
    complectation = models.TextField(blank=True, verbose_name='Комлектация товара')
    certificate_diller = models.FileField(upload_to='certificates/', blank=True, null=True, verbose_name='Сертификат 1')
    certificate_two = models.FileField(upload_to='certificates/', blank=True, null=True, verbose_name='Сертификат 2')
    certificate_tree = models.FileField(upload_to='certificates/', blank=True, null=True, verbose_name='Сертификат 3')
    guarantee = models.FileField(upload_to='guaranties/', blank=True, null=True, verbose_name='Гарантия товара')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.CharField(choices=AvailabilityChoices.choices, default = AvailabilityChoices.IN_STOCK, verbose_name='Доступность')
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
        return reverse("main:detail_product", args=[self.slug])
    

    def save(self, *args, **kwargs):
        for field_name in ['image_1', 'image_2', 'image_3']:
            image = getattr(self, field_name)
            if image and not image.name.endswith('.webp'):
                try:
                    compressed = compress_image(image)
                    compressed.name = f'compressed_{image.name}'
                    setattr(self, field_name, compressed)
                except Exception as err:
                    print(f'Error at compress: {field_name}: {err}')
        super().save(*args, **kwargs)


class Favorite(models.Model):
    session_key = models.CharField(max_length=1024, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('session_key', 'product')
