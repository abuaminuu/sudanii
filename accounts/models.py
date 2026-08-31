from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    roles = (
        ("admin","Admin"),
        ("vendor","Vendor"),
        ("customer","Customer"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=32, choices=roles, default="customer")
    picture = models.ImageField(upload_to="accounts/profile/", null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} {self.role}"

