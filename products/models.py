from django.db import models
from uuid import uuid4
from django.utils.text import slugify
from accounts.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

# products category model
class Category(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True)

    

class Product(models.Model):
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # override save method
    def save(self, *args, **kwargs):
        # if no slug
        if not self.slug:
            slug = slugify(self.name)
            # gen 6-hex values
            ghex = uuid4().hex[:6]
            self.slug = f"{slug}-{ghex}"

        # save method to commit to database
        super().save(*args, **kwargs)
        
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/images/")
    is_primary = models.BooleanField(default=False)

    """
    The Edge Case: If you upload 4 images and all default to is_primary=True, 
    your database will store multiple primary images for one product.
    The Rule: You will need custom logic in save() or in the Serializer 
    to ensure that when an image is set to is_primary=True, all other images 
    for that product are flipped to is_primary=False.
    """
    def save(self, *args, **kwargs):

        # 1. Check if the product already has any primary image:
        has_primary = ProductImage.objects.filter(product=self.product, is_primary=True).exists()

        # 2. If no primary image exists yet, Force self.is_primary = True
        if not has_primary:
            self.is_primary = True
            

        # 3. Call super().save(*args, **kwargs) first to guarantee self.id exist fpr later use
        super().save(*args, **kwargs)

        # 4. If self.is_primary is True, filter(product=self.product).exclude(id=self.id).update(is_primary=False)
        if self.is_primary:
            ProductImage.objects.filter(product=self.product).exclude(id=self.id).update(is_primary=False)
