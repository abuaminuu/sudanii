from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    roles = (
        ("Admin","admin"),
        ("Vendor","vendor"),
        ("Customer","customer"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=8, choices=roles, default="customer")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} {self.role}"
