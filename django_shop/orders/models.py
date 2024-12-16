###Models в приложении Orders в проекте django_shop
from django.contrib.auth.models import User
from django.db import models
from shop.models import Product


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
        null=True,
        blank=True  # Если требуется разрешить создание заказа без пользователя
    )
    first_name = models.CharField(max_length=60, verbose_name="Имя")
    last_name = models.CharField(max_length=60, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Email")
    address = models.CharField(max_length=150, verbose_name="Адрес")
    postal_code = models.CharField(max_length=30, verbose_name="Почтовый индекс")
    city = models.CharField(max_length=100, verbose_name="Город")
    updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    paid = models.BooleanField(default=False, verbose_name="Оплачен ли заказ")

    class Meta:
        ordering = ('-created',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity
