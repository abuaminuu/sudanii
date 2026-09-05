from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from products.models import Product

@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Invalidate the cache for the product list and product detail views
    when a Product instance is created or updated or deleted.
    """
    # Invalidate the product list cache
    cache.delete_pattern('views.decorators.cache.cache_page.*')

    # Invalidate the product detail cache for this specific product
    cache.delete_pattern("*:views.decorators.cache.cache_page")