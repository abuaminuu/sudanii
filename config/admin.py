from django.contrib import admin

from accounts.models import User
from products.models import Product, ProductImage
from orders.models import Order, OrderItem

admin.site.regsiter(User)
admin.site.regsiter(Product)
admin.site.regsiter(ProductImage)
admin.site.regsiter(Order)
admin.site.regsiter(OrderItem)
