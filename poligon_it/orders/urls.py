from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('quick_order/', views.quick_order, name="quick_order"),
]
