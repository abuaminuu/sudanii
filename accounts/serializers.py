from rest_framework import serializers
from accounts.models import User
from rest_framework.validators import ValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):

    # modify password to conform certain validation
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "picture"]

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("duplicate email")
        return email

    def validate_role(self, value):
        if value == "admin":
            raise ValidationError("you can not register directly as admin !!!")
        return value
    
    
    def create(self, validated_data):
        # extract text password from data recieved
        password = validated_data.pop("password")

        # instantiate user
        user = User(**validated_data)

        # hash password secuely
        user.set_password(password)
        user.save()

        return user

class UserPublicSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "picture"]
        read_only_fields = ["id", "username", "email", "role", "picture"]
