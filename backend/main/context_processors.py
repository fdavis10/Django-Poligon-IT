from .models import Product, Favorite
from .models import Category, Subcategory_1
from django.db.models import Prefetch

def favorites_processor(request):
    session_key = request.session.session_key
    favorites_ids = Favorite.objects.filter(session_key=session_key).values_list('product_id', flat=True) if session_key else []
    favorites = Product.objects.filter(id__in=favorites_ids)
    favorites_count = favorites.count()
    return {'favorites':favorites, 'favorites_count':favorites_count}

def category_context(request):
    categories = Category.objects.all()
    subcategories = Subcategory_1.objects.all()
    return{
        'categories': categories,
        'subcategories': subcategories,
    }