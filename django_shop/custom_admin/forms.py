from django import forms
from orders.models import Order, OrderItem
from shop.models import Category, Filters, Product, Review, Tag

# Формы для CRUD операций


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class FilterForm(forms.ModelForm):
    class Meta:
        model = Filters
        fields = "__all__"


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = "__all__"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = "__all__"
