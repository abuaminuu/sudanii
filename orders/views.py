from django.shortcuts import render
from rest_framework import viewsets
from orders.models import Order
from orders.serializers import OrderSerializer
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "admin":
            return Order.objects.prefetch_related("items__product").all()

        # else user must be customer or vendor
        return Order.objects.filter(customer=user).prefetch_related("items__product").all()
    
