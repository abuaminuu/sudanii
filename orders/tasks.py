from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from django.core.mail import send_mail
from orders.models import Order
from products.models import Product
from django.conf import settings
from django.db import transaction

@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.select_related("customer").prefetch_related("items__product").get(id=order_id)
        subject = f"Order Confirmation - Order #{order.id}"
        recipient_email = order.customer.email

        # format item breakdown 
        item_list = "\n".join([
            f"- {item.product.name} x {item.quantity} @ {item.price}"
            for item in order.items.all()
        ])

        message = (
            f"Hello {order.customer.username},\n\n"
            f"Thank you for your order!\n\n"
            f"Order Summary:\n"
            f"{item_list}\n\n"
            f"Total Amount: ${order.total_price}\n"
            f"Status: {order.status.capitalize()}\n\n"
            f"We will notify you once your items ship."
        )
       
        # send the email using Django's send_mail function
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False
        )
        
        # return a message indicating the email was sent successfully
        return f"Order confirmation email sent to {recipient_email} for order #{order.id}"
    except Order.DoesNotExist:
        return f"Order with ID {order_id} does not exist."
    

@shared_task
def cancel_stale_unpaid_orders():
    expiration_cutoff = timezone.now() - timedelta(hours=24)

    # get pending orders created before cutoff time
    stale_orders = Order.objects.filter(status="pending", created_at__lte=expiration_cutoff).prefetch_related("items__products")

    # track number of orders cancelled
    cancelled_count = 0

    # cancel each stale order and update its status
    for order in stale_orders:
        # refresh the order instance to avoid stale data issues
        order.refresh_from_db()
        with transaction.atomic():
            # re fetch with row locking to prevent race conditions
            order = Order.objects.select_for_update().get(id=order.id)

            # double check if the order is still pending before cancelling
            if order.status != "pending":
                # skip if the order is no longer pending
                continue  

            # restore stocks for each item in the order
            for item in order.items.all():
                # lock the product row to prevent race conditions
                product = Product.objects.select_for_update().get(id=item.product.id)
                product.stock += item.quantity
                product.save()            

            # mark the order as cancelled
            order.status = "cancelled"
            order.save()
            cancelled_count += 1

    return f"Cancelled {cancelled_count} stale unpaid orders withing last 24 hours."
