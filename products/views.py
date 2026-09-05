from django.shortcuts import render
from rest_framework import viewsets
from products.models import Category, Product
from products.serializers import CategorySerializer, ProductSerializer
from products.permissions import IsVendorOrReadonly, IsAdminUserOrReadOnly
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie


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

    # Cache Product List endpoint for 15 minutes (Includes filter & cursor params)
    @method_decorator(cache_page(60 * 15))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # inject merchant 
    def perform_create(self, serializer):
        # Automatically set merchant to the authenticated user sending the POST request
        serializer.save(merchant=self.request.user)
    