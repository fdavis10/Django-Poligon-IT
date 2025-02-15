from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.index_page, name="index_page"),
    path('category/<slug:slug>/', views.product_list_by_category, name='product_list_by_category'),
    path('subcategory/<slug:slug>', views.product_list_by_subcategory, name='product_list_by_subcategory'),
    path('sub_subcategory/<slug:slug>/', views.product_list_by_sub_subcategory, name='product_list_by_sub_subcategory'),
    path('product/<slug:slug>', views.detail_product, name='detail_product'),
]


