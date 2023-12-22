from rest_framework import serializers
from authentication.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator

# ModelSerializer - As we want to work with User Model
class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "password"
        ]

        # use this to define which variables are read only and write_only
        extra_kwargs = {
            "password": {"write_only": True},
            'email':{
                'validators': [EmailValidator]
            }
        }

    # It do not perform validations by default, so we can implement if we want
    # Some more validations
    # naming convention - validate_ followed by field name
    def validate_password(self, value):
        validate_password(value)   
        return value
    
    def validate_email(self, value):
        lower_case_email = value.lower()
        return lower_case_email

class UserLoginSerializer(serializers.ModelSerializer):
    username_or_email =  serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            "username_or_email",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "is_superuser"
        )
        read_only_fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "is_superuser"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }
    
    def validate_username_or_email(self, value):
        return value.lower()