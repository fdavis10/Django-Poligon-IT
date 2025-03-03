from django.db import models
from main.models import Product
from django.conf import settings

class Order(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя клиента')
    last_name = models.CharField(max_lenght=50, verbose_name='Фамилия клиента')
    email = models.EmailField(verbose_name='Почта клиента')
    city = models.CharField(max_length=100, verbose_name='Город клиента')
    address = models.CharField(max_length=250, verbose_name='Адрес клиента')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Изменен')
    is_paid = models.BooleanField(default=False, verbose_name='Статус заказа')

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return self.id
    
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