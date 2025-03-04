from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'phone_number', 'email']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request:
            self.initial['first_name'] = self.request.GET.get('first_name', '')
            self.initial['phone_number'] = self.request.GET.get('phone_number', '')
            self.initial['email'] = self.request.GET.get('email ', '')
    
    def save(self, commit=True):
        order = super().save(commit=False)
        if commit:
            order.save()
        return order



    