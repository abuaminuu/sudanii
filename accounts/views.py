from django.shortcuts import render
from rest_framework import viewsets, generics
from accounts.serializers import UserRegistrationSerializer
from rest_framework.permissions import AllowAny

# Create your views here.
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
