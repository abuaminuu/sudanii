# conftest.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def vendor_user(db):
    return User.objects.create_user(
        username="test_vendor",
        email="vendor@example.com",
        password="password123",
        role="vendor"
    )

@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        username="test_customer",
        email="customer@example.com",
        password="password123",
        role="customer"
    )

@pytest.fixture
def category(db):
    return Category.objects.create(name="Electronics", slug="electronics")

@pytest.fixture
def sample_product(db, vendor_user, category):
    return Product.objects.create(
        merchant=vendor_user,
        category=category,
        name="Wireless Mouse",
        slug="wireless-mouse",
        description="Ergonomic mouse",
        price=25.00,
        stock=100
    )
