from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import notify_telegram
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO


def generate_order_pdf(order, order_items):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    font_path = "static/fonts/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVu", font_path))
    pdf.setFont("DejaVu", 12)
    pdf.drawString(100, 800, f'Чек заказа №{order.id}')

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 770, f'Имя клиента: {order.first_name}')
    pdf.drawString(100, 750, f'Email: {order.email}')
    pdf.drawString(100, 730, f'Телефон: {order.phone_number}')

    pdf.setFont('Helvetica', 12)
    pdf.drawString(100, 700, "Состав заказа:")

    y_position = 680
    pdf.setFont('Helvetica', 12)
    for item in order_items:
        pdf.drawString(120, y_position, f'- {item.product.name}: {item.quantity} шт. - {item.price} руб.')
        y_position -= 20
    
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(100, y_position-20, f'Общая сумма: {order.get_total_cost()} руб.')

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer

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
        
        pdf_buffer = generate_order_pdf(order, order_items)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'
        return response
    else:
        print(f'В форме создания заказа ошибка: {form.errors}')
    return render(request,
                    'orders/order/create.html',
                    {'cart':cart,
                    'form':form})