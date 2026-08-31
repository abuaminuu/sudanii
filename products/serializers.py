from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from products.models import Product, ProductImage, Category

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model =  ProductImage
        fields = ["id", "image", "is_primary"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent_category"]

class ProductSerializer(serializers.ModelSerializer):

    # Display related images as a nested list in response JSON
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Prevent client from specifying or tampering with these fields during POST/PUT
    merchant = serializers.ReadOnlyField()
    slug = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'merchant', 'category', 'name', 'slug', 'description', 'price', 'stock', 'images', 'created_at']

    def validate_price(self, value):
        if value <= 0:
            raise ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        if value< 0:
            raise ValidationError("Stock cannot be negative.")
        return value

    