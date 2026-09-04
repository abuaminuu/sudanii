from django.shortcuts import render
from rest_framework import viewsets
from orders.models import Order
from orders.serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
from rest_framework.views import APIView
from django.db import transaction
from uuid import uuid4


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
    
    @action(detail=True, methods=['POST'], url_path='pay')
    def pay(self, request, pk=None):
        """
        POST /api/orders/{id}/pay/
        Generates a Flutterwave checkout link for pending orders.
        """
        order = self.get_object()

        if order.status != 'pending':
            return Response(
                {"error": f"Cannot pay for order with status '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # return Response({
        #     "message": f"step 1- {uuid4().hex} checkout URL.",
        # })
    
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        # return Response({
        #     "message": f"step 2- {uuid4().hex} checkout URL.",
        # })

        # Unique transaction reference
        tx_ref = f"{order.id}:{uuid4().hex}"
        
        payload = {
            "tx_ref": tx_ref,
            "amount": str(order.total_price),
            "currency": "NGN",
            "redirect_url": "http://127.0.0.1:8000/api/orders/payment-callback/",
            "customer": {
                "email": order.customer.email,
                "username": order.customer.username
            },
            "customizations": {
                "title": "Multi-Vendor Store Checkout",
                "description": f"Payment for Order #{order.id}"
            },
            "meta": {
                "order_id": order.id
            }
        }
    
        # return Response({
        #     "message": f"step 3- {uuid4().hex} checkout URL.",
        # })
    
        try:
            response = requests.post(
                "https://api.flutterwave.com/v3/payments/",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            data = response.json()

            if response.status_code == 200 and data.get("status") == "success":
                return Response({
                    "checkout_url": data["data"]["link"],
                    "tx_ref": payload["tx_ref"]
                }, status=status.HTTP_200_OK)

            return Response(
                {"error": "Failed to generate payment link from provider", "details": data},
                status=status.HTTP_502_BAD_GATEWAY
            )

        except requests.exceptions.RequestException as e:
            return Response({"error": "Payment gateway unreachable", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({
            "message": f"step 2- {uuid4().hex} checkout URL.",
        })

class PaymentWebhookView(APIView):
    """
    POST /api/orders/webhook/
    Webhook listener for payment success notifications.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Verify Secret Hash Header for Security
        signature = request.headers.get("verif-hash")
        if not signature or signature != settings.FLUTTERWAVE_SECRET_HASH:
            return Response({"error": "Invalid signature hash"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = request.data
        event = payload.get("event")

        # Process Successful Charge Events
        if event == "charge.completed" and payload.get("data", {}).get("status") == "successful":
            data = payload["data"]
            order_id = data.get("meta", {}).get("order_id")
            charged_amount = float(data.get("amount", 0))

            if order_id:
                try:
                    with transaction.atomic():
                        order = Order.objects.select_for_update().get(id=order_id)

                        # Verify price paid matches order total before updating
                        if order.status == 'pending' and charged_amount >= float(order.total_price):
                            order.status = 'paid'
                            order.save()

                    return Response({"status": "Order status updated to paid"}, status=status.HTTP_200_OK)

                except Order.DoesNotExist:
                    return Response({"error": f"Order #{order_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"status": "Event received but ignored"}, status=status.HTTP_200_OK)
    
