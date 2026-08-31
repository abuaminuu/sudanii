from django.shortcuts import render
from rest_framework import viewsets
from products.models import Category, Product
from products.serializers import CategorySerializer, ProductSerializer
from products.permissions import IsVendorOrReadonly, IsAdminUserOrReadOnly

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    # fetch all categiries
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # restric modifications to admins, GET for everyone
    permission_classes = [IsAdminUserOrReadOnly]


class ProductViewSet (viewsets.ModelViewSet):

    # JOIN 'category' and 'merchant' in 1 query, then 1 Executes extra optimized query to batch-fetch all related 'images'
    queryset = Product.objects.select_related('category', 'merchant').prefetch_related('images').all()
    
    serializer_class = ProductSerializer
    permission_classes = [IsVendorOrReadonly]

    # inject merchant 
    def perform_create(self, serializer):
        # Automatically set merchant to the authenticated user sending the POST request
        serializer.save(merchant=self.request.user)
    