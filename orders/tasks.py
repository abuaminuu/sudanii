from celery import shared_task
from django.core.mail import send_mail
from orders.models import Order
from django.conf import settings

@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.select_related("customer").prefetch_related("items__products").get(id=order_id)
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
    