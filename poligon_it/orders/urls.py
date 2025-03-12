from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('quick_order/', views.quick_order, name="quick_order"),
    path('api/orders/', views.get_orders, name="get_orders"),
    path('api/orders/<int:order_id>/', views.get_order_detail, name="get_order_detail")
]
