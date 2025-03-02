from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from main.models import Product
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'])
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    action = request.POST.get('action')
    if action == 'increase':
        cart.add(product=product, quantity=1)
    elif action == 'decrease':
        cart.add(product=product, quantity=-1)
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id = product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    cart_items = list(cart)
    total_price = sum(item['quantity'] * item['product'].price for item in cart)
    return render(request, 'cart/cart_detail.html', {'cart_items':cart_items, 'total_price':total_price})