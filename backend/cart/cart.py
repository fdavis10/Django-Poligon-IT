from decimal import Decimal
from django.conf import settings
from main.models import Product
from decimal import Decimal, InvalidOperation

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity = 1, update_quantity=False):

        if product.price_on_request:
            return

        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if update_quantity:
            self.cart[product_id]['quantity'] = max(1, quantity)
        else:
            new_quantity = self.cart[product_id]['quantity'] + quantity
            self.cart[product_id]['quantity'] = max(1, new_quantity)
        self.save()
    
    def save(self):
        self.session.modified = True

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            try:
                item['price'] =Decimal(item['price'])
                item['total_price'] = item['price']*item['quantity']
                yield item
            except (TypeError, ValueError, InvalidOperation):
                continue
        
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        # total = sum(item['quantity']*item['product'].price for item in self.cart.values())
        total = Decimal('0.0')
        for item in self:
            try:
                total += item['total_price']
            except (KeyError, InvalidOperation):
                continue
        return format(total, '.2f')



