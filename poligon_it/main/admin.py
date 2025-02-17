from django.contrib import admin
from .models import Category, Subcategory_1, Subcategory_2, Product, Specifications, ProductSpecification

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Subcategory_1)
class SubCategory1Admin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'category__name')

@admin.register(Subcategory_2)
class Subcategory2Admin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'category_main', 'slug')
    prepopulated_fields = {'slug':('name',)}
    search_fields = ('name', 'subcategory__name', 'category_main__name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available', 'available_quantity', 'created', 'description')
    list_filter = ('category', 'available', 'created', 'updated',)
    search_fields = ('name', 'descriprion', 'category__name')
    prepopulated_fields = {'slug':('name',)}

@admin.register(Specifications)
class SpecificationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'specification', 'value')
    search_fields = ('product__name', 'specification__name', 'value')
