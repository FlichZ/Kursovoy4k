from django.contrib import admin
from shop.models import Category, Tag, Product

# Здесь можно добавить кастомное администрирование
# Но для этого проекта мы используем свой собственный интерфейс
admin.site.site_header = "Custom Admin Panel"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Welcome to the Custom Admin Panel"
