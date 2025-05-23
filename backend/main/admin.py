from django.contrib import admin, messages
from .models import Category, Subcategory_1, Product
from django_json_widget.widgets import JSONEditorWidget
from django.db import models


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk','name', 'category', 'price', 'available', 'available_quantity', 'created', 'description')
    list_filter = ('category', 'available', 'created', 'updated',)
    search_fields = ('name', 'descriprion', 'category__name')
    prepopulated_fields = {'slug':('name',)}
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
