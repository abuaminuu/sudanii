from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import OrderViewSet

router = DefaultRouter()

router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("orders/webhook/", OrderViewSet.as_view(), name="payment-webhook"),
    path("", include(router.urls))
]
