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
    removed_items = request.session.get('removed_items', [])
    removed_items.append({'id':product.id, 'name':product.name, 'price':float(product.price)})
    request.session['removed_items'] = removed_items
    request.session.modified = True
    return redirect('cart:cart_detail')


@require_POST
def cart_restore(request, product_id):
    cart = Cart(request)
    removed_items = request.session.get('removed_items', [])
    restored_item = None
    for item in removed_items:
        if item['id'] == product_id:
            restored_item = item
            break
    if restored_item:
        product = get_object_or_404(Product, id=restored_item['id'])
        cart.add(product=product, quantity=1)
        removed_items.remove(restored_item)

    request.session['removed_items'] = removed_items
    request.session.modified = True
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    cart_items = list(cart)
    total_price = sum(item['quantity'] * item['product'].price for item in cart)
    return render(request, 'cart/cart_detail.html', {'cart_items':cart_items, 'total_price':total_price})