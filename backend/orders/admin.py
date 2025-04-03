from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    search_fields = ('first_name', 'email', 'phone_number')
    actions = ['mark_approved']

    def mark_approved(self, request, queryset):
        for order in queryset:
            order.status_of_order == Order.STATUS_APPROVED
            order.save()

    mark_approved.short_description = "✅ Потвердить выбранные заказы!"
    # inlines = []

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    if instance.status_of_order == Order.STATUS_APPROVED and instance.is_paid:
        from .tasks import send_order_email_task
        send_order_email_task.delay(instance.id)