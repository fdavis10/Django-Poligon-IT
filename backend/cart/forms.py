from django import forms

PRODUCT_QUANTITY_CHOISES = [(i, str(i)) for i  in range(1, 11)]

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices= PRODUCT_QUANTITY_CHOISES, coerce=int)
    
    def __init__(self, *args, **kwargs):
        max_quantity = kwargs.pop('max_quantity', 10)
        super().__init__(*args, **kwargs)
        self.fields['quantity'].choices = [(i, str(i)) for i  in range(1, max_quantity + 1)]
        