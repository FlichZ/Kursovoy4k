from django.urls import path

from . import views
from .views import (backup_db, generate_report, restore_db, user_create,
                    user_delete, user_edit, user_list)

app_name = "custom_admin"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("backup/", backup_db, name="backup_db"),
    path("restore/", restore_db, name="restore_db"),
    path("generate-report/", generate_report, name="generate_report"),
    # Продукты
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/edit/<int:pk>/", views.product_edit, name="product_edit"),
    path("products/delete/<int:pk>/", views.product_delete, name="product_delete"),
    # Фильтры
    path("filters/", views.filter_list, name="filter_list"),
    path("filters/create/", views.filter_create, name="filter_create"),
    path("filters/edit/<int:pk>/", views.filter_edit, name="filter_edit"),
    path("filters/delete/<int:pk>/", views.filter_delete, name="filter_delete"),
    # Теги
    path("tags/", views.tag_list, name="tag_list"),
    path("tags/create/", views.tag_create, name="tag_create"),
    path("tags/edit/<int:pk>/", views.tag_edit, name="tag_edit"),
    path("tags/delete/<int:pk>/", views.tag_delete, name="tag_delete"),
    # Отзывы
    path("reviews/", views.review_list, name="review_list"),
    path("reviews/create/", views.review_create, name="review_create"),
    path("reviews/edit/<int:pk>/", views.review_edit, name="review_edit"),
    path("reviews/delete/<int:pk>/", views.review_delete, name="review_delete"),
    # Категории
    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/edit/<int:id>/", views.category_edit, name="category_edit"),
    path("categories/delete/<int:id>/", views.category_delete, name="category_delete"),
    # Заказы
    path("orders/", views.order_list, name="order_list"),
    path("orders/edit/<int:id>/", views.order_edit, name="order_edit"),
    path("orders/delete/<int:id>/", views.order_delete, name="order_delete"),
    # Заказанные товары (OrderItems)
    path("orderitems/", views.orderitem_list, name="orderitem_list"),
    path("orderitems/edit/<int:id>/", views.orderitem_edit, name="orderitem_edit"),
    path(
        "orderitems/delete/<int:id>/", views.orderitem_delete, name="orderitem_delete"
    ),
    path("users/", user_list, name="user_list"),
    path("users/create/", user_create, name="user_create"),
    path("users/<int:pk>/edit/", user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", user_delete, name="user_delete"),
    path("", views.dashboard, name="dashboard"),
]
