from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        
        # Ensure username is set if required by model, else gen from email
        if "username" not in extra_fields or not extra_fields["username"]:
            extra_fields["username"] = email.split("@")[0]

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        # validate checks
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)

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

    objects = CustomUserManager()

    class Meta:
        indexes = [
            models.Index(fields=["email"], name="user_email_index")
        ]
    def __str__(self):
        return f"{self.email} {self.role}"

