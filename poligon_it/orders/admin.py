from django.contrib import admin
from .models import Order, OrderItem
from django.utils.safestring import mark_safe

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name',
        'email',
        'status_of_order',
        'is_paid',
    ]
    list_filter = [
        'is_paid',
        'created',
        'updated',
    ]
    # inlines = []