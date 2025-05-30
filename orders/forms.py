from django import forms
from django.forms import inlineformset_factory

from .models import Order, OrderItem
from customers.models import Customer
from products.models import Product


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer', 'status', 'payment_method',
            'shipping_address', 'discount', 'tax',
            'shipping_cost', 'notes'
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'discount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)

        # If we're editing an existing item, don't change the product
        if self.instance and self.instance.pk:
            self.fields['product'].disabled = True


OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem, form=OrderItemForm,
    extra=1, can_delete=True
)
# orders/forms.py
OrderItemFormOrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    fields=['product', 'quantity', 'price'],
    extra=0,            # qo‘shimcha bo‘sh satr ko‘rsatmaslik
    can_delete=True,    # DELETE katakchasi ishlashi uchun
    min_num=1,
    validate_min=True
)

