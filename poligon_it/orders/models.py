from django.db import models
from main.models import Product
from django.conf import settings

class Order(models.Model):

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидание'),
        (STATUS_APPROVED, 'Потвержден'),
        (STATUS_REJECTED, 'Отклонен'),
    ]

    first_name = models.CharField(max_length=256, verbose_name='Имя клиента') 
    phone_number = models.CharField(max_length=256, verbose_name='Номер телефона')
    email = models.EmailField(verbose_name='Почта клиента') 
    status_of_order = models.CharField(max_length=20, choices=STATUS_CHOICES, default = STATUS_PENDING)
    is_paid = models.BooleanField(default=False, verbose_name='Статус оплаты')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return self.status_of_order
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)


    def __str__(self):
        return str(self.id)
    
    def get_cost(self):
        return self.price * self.quantity