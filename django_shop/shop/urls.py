from django.urls import include, path
from rest_framework import routers

from .views import CategoryViewSet, FeedbackFormView, FiltersViewSet, LoginUser, ProductDetailView, ProductViewSet, RegisterUser, ReviewViewSet, ShopCategory, ShopHome, TagViewSet, about, logout_user, my_orders, pay_order

router = routers.DefaultRouter()
router.register(r"filters", FiltersViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"tags", TagViewSet)
router.register(r"products", ProductViewSet)
router.register(r"reviews", ReviewViewSet)

# используем namespacing для удобства. Теперь, к примеру, the product_list URL будет доступен, как shop:product_list в других частях Django проекта.
app_name = "shop"

urlpatterns = [
    path("", ShopHome.as_view(), name="product_list"),
    path(
        "category/<slug:category_slug>/",
        ShopCategory.as_view(),
        name="product_list_by_category",
    ),
    path(
        "category/<slug:category_slug>/<slug:slug>",
        ProductDetailView.as_view(),
        name="product_detail",
    ),
    path("about/", about, name="about"),
    path("feedback/", FeedbackFormView.as_view(), name="feedback"),
    path("login/", LoginUser.as_view(), name="login"),
    path("logout/", logout_user, name="logout"),
    path("register/", RegisterUser.as_view(), name="register"),
    path("api/", include(router.urls)),
    path("my-orders/", my_orders, name="my_orders"),
    path("pay-order/<int:order_id>/", pay_order, name="pay_order"),
]
