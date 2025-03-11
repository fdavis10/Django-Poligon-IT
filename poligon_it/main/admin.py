from django.contrib import admin, messages
from .models import Category, Subcategory_1, Product
from django_json_widget.widgets import JSONEditorWidget
from django.db import models
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.html import format_html
from .tasks import import_product_from_1c

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
    list_display = ('name', 'category', 'price', 'available', 'available_quantity', 'created', 'description','sync_with_1c_button')
    list_filter = ('category', 'available', 'created', 'updated',)
    search_fields = ('name', 'descriprion', 'category__name')
    prepopulated_fields = {'slug':('name',)}
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def sync_with_1c_button(self, obj):
        return format_html(
            '<a class="button" href="{}">🔄 Обновить товары из 1С</a>',
            "/crm/main/sync-1c/"
        )
    sync_with_1c_button.short_description = "Синхронизация"
    sync_with_1c_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sync-1c/', self.sync_products_from_1c, name="sync_products_from_1c"),
        ]
        return custom_urls + urls
    
    def sync_products_from_1c(self, request):
        import_product_from_1c.delay()
        self.message_user(request, '🔄 Импорт товаров из 1С запущен!', messages.SUCCESS)
        return redirect(reverse('admin:main_product_changelist'))



