from rest_framework import serializers
from orders.models import Order, OrderItem
from django.db import transaction
from products.models import Product
from orders.tasks import send_order_confirmation_email


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = ['price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order

        fields = ['id', 'customer', 'status', 'total_price', 'items', 'created_at']
        read_only_fields = ['customer', 'status', 'total_price', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        # Wrap everything in an atomic transaction block
        with transaction.atomic():
            # Create the base Order instance
            order = Order.objects.create(customer=user, status='pending', total_price=0)
            calculated_total = 0

            for item in items_data:
                # Lock row for update to prevent race conditions during concurrent checkouts
                product_obj = Product.objects.select_for_update().get(pk=item["product"].pk)
                requested_qty = item['quantity']

                # Validate stock availability
                if product_obj.stock < requested_qty:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product_obj.name}. Available: {product_obj.stock}"
                    )

                # Deduct stock atomically
                product_obj.stock -= requested_qty
                product_obj.save()

                # 5. Capture current price snapshot & add to order items
                unit_price = product_obj.price
                calculated_total += unit_price * requested_qty

                OrderItem.objects.create(
                    order=order,
                    product=product_obj,
                    quantity=requested_qty,
                    price=unit_price
                )

            # 6. Save accumulated total to the parent Order
            order.total_price = calculated_total
            order.save()
            
            # Trigger Celery task asynchronously ONLY after DB commit succeeds
            transaction.on_commit(lambda: send_order_confirmation_email.delay(order.id))
            return order
    