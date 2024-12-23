"""Реализация настройки конфигурации для приложения shop."""
from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # задает, какой тип автоинкрементного поля будет использоваться
    # по умолчанию для всех моделей в данном приложении. Если PK не задан-будет использоваться PK типа BigAutoField
    name = "shop"
    verbose_name = "eSports"  # это имя может быть использовано в разных модулях Джанго, в том числе для отображения в админке
    # сработает только если мы зарегистрируем наше приложение в settings  с использованием ShopConfig
