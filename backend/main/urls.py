from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.index_page, name="index_page"),
    path('about_us/', views.about_us, name='about_us'),
    path('guarantee/', views.guarentee, name='guarentee'),
    path('category/<slug:slug>/', views.product_list_by_category, name='product_list_by_category'),
    path('contacts/', views.contacts, name='contacts'),
    path('category/<slug:category_slug>/subcategory/<slug:subcategory_slug>/', views.product_list_by_subcategory, name='product_list_by_subcategory'),
    path('product/<slug:slug>/', views.detail_product, name='detail_product'),
    path('favorites/', views.favorites_list, name='favorite_list'),
    path('favorites/add/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/clear/', views.clear_favorites, name='clear_favorites'),
    path('search/', views.search_result, name='search_results'),
    path('mobile_search/', views.mobile_search, name='mobile_search'),
    path('api/products/', views.product_list, name="product_list"),
    path('api/categories/', views.get_categories, name='get_categories'),
    path('api/subcategories', views.get_subcategories, name='get_subcategories'),
    path('upload/', views.upload_products, name='upload_products'),
    path('download_all_docs/<int:product_id>/', views.download_all_docs, name='download_all_docs'),
    
]


