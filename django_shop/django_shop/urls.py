###URL в приложении django_shop в проекте django_shop
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('cart/', include('cart.urls', namespace='cart')),
                  path('orders/', include('orders.urls')),
                  path('custom-admin/', include('custom_admin.urls')),  # добавьте путь для вашего кастомного админки
                  path('captcha/', include('captcha.urls')),
                  path('', include('shop.urls', namespace='shop')),  # копируем все urls из приложения shop
                  path('api-auth/', include('rest_framework.urls'))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
