from django.shortcuts import render, redirect
from django.urls import reverse
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import notify_telegram

def order_create(request):
    cart = Cart(request)
    form = OrderCreateForm(request.POST or None, request=request)

    if request.method == "POST" and form.is_valid():
        order = form.save()
        order_items = []
        print(f'Заказ успешно создан: {order.id}')
        notify_telegram.delay(order.id)
        for item in cart:
            product = item['product']
            price = product.price
            order_item = OrderItem.objects.create(
                order=order,
                product = item['product'],
                price = price,
                quantity = item['quantity']
            )
            order_items.append(order_item)
        cart.clear()
        request.session['order_id'] = order.id
        return render(request, 'orders/order/checkout.html',{
            'order': order,
            'order_items': order_items,
            'cart': cart
        })
    else:
        print(f'В форме создания заказа ошибка: {form.errors}')
    return render(request,
                    'orders/order/create.html',
                    {'cart':cart,
                    'form':form})