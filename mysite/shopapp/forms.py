from django.forms import ModelForm
from django.contrib.auth.models import Group
from django.core import validators
from .models import Product, Order


# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     price = forms.DecimalField(min_value=1, max_value=100000, decimal_places=2)
#     description = forms.CharField(
#         widget=forms.Textarea(attrs={"rows": "5", "cols": "30"}),
#         label="Product description",
#         validators=[validators.RegexValidator(
#             regex=r"great", message="Field must contain word 'great'",
#
#         )],
#     )

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount"


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = "delivery_address", "promocode", "user", "products"


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
