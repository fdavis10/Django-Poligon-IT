from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
import openpyxl.writer
from main.models import Product
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import notify_telegram
from io import BytesIO
import openpyxl


def generate_order_excel(order, order_items):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Заказ_{order.id}"

    ws.append(['Номер заказа', order.id])
    ws.append(['Дата', order.created.strftime("%Y-%m-%d %H:%M")])
    ws.append(['Клиент', order.first_name])
    ws.append(['Email', order.email])
    ws.append(['Номер телефона', order.phone_number])
    ws.append([])
    ws.append(['Наименование', 'Код товара', 'Цена за 1 шт.', 'Количество', 'Стоимость'])

    for item in order_items:
        ws.append([
            item.product.name,
            item.product.id,
            item.price,
            item.quantity,
            item.price * item.quantity
        ])

    ws.append([])
    ws.append(['Итого', '', '', '', order.get_total_cost()])

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    return file_stream


# def send_order_email(order):
#     order_items = order.items.all()
#     excel_file = generate_order_excel(order, order_items)

#     subject = f'Ваш заказ №{order.id} потвержден!'
#     message = (
#         f'Здравствуйте, {order.first_name}!\n\n'
#         f'Ваш заказ №{order.id} потвержден. Таблица с деталями во вложении.\n'
#         f'Для дальнейшей информации обращайтесь по телефону!'
#     )

#     recipient_list = [order.email]

#     email = EmailMessage(
#         subject=subject,
#         body=message,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=recipient_list,
#     )

#     email.attach(f'Заказ_{order.id}.xlsx', excel_file.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     email.send()


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
        # send_order_email(order)
        return render(request, 'orders/order/created.html')
    else:
        print(f'В форме создания заказа ошибка: {form.errors}')
    return render(request,
                    'orders/order/create.html',
                    {'cart':cart,
                    'form':form})


def quick_order(request):
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        if form.is_valid() and product_id:
            product = get_object_or_404(Product, id=product_id)
            order = form.save()

            OrderItem.objects.create(order=order, product=product, price = product.price, quantity=quantity)
            notify_telegram.delay(order.id)
            
            return JsonResponse({"status":"succes", "message": "Ваш заказ успешно оформлен!"})
        return JsonResponse({"status":"error", "message":"Ошибка в данных формы!"}, status=400)
    return JsonResponse({"status":"error", "message":"Неверный метод запроса!"}, status=405)