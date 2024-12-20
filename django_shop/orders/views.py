from cart.cart_services import Cart
from cart.views import render
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from rest_framework import viewsets

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .permissions import IsStaffOrReadOnly
from .serializers import OrderItemSerializer, OrderSerializer


@login_required  # Убедитесь, что пользователь авторизован
def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Создание заказа с привязкой к пользователю
            order = form.save(commit=False)
            order.user = request.user  # Привязка к текущему пользователю
            order.save()

            # Создание OrderItem для каждого элемента корзины
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            cart.clear_cart()
            send_mail(
                "Заказ Оформлен",
                "Войдите в админ панель, чтобы просмотреть новый заказ.",
                "example@example.com",
                ["example@example.com"],
                fail_silently=True,
            )
            return render(request, "orders/created.html", {"order": order})
    else:
        form = OrderCreateForm()
    return render(request, "orders/create.html", {"form": form})


class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    permission_classes = [IsStaffOrReadOnly]


class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    permission_classes = [IsStaffOrReadOnly]


class OrderCreateView(CreateView):
    model = Order
    template_name = "orders/order_form.html"
    fields = ["first_name", "last_name", "email", "address", "postal_code", "city"]
    success_url = reverse_lazy("shop:product_list")
    permission_classes = [IsStaffOrReadOnly]


class OrderUpdateView(UpdateView):
    model = Order
    template_name = "orders/order_form.html"
    fields = ["first_name", "last_name", "email", "address", "postal_code", "city"]
    success_url = reverse_lazy("orders:order_list")
    permission_classes = [IsStaffOrReadOnly]


class OrderDeleteView(DeleteView):
    model = Order
    template_name = "orders/order_confirm_delete.html"
    success_url = reverse_lazy("orders:order_list")
    permission_classes = [IsStaffOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsStaffOrReadOnly]
