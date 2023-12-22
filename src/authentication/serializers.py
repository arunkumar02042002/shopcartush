from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.utils import datetime_from_epoch

from authentication.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from django.conf import settings

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
    

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs["refresh"])
            data = {"access": str(refresh.access_token)}
            if settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]:
                payload = refresh.payload
                id = payload["user_id"]
                user = User.objects.get(id=id)
                if not settings.ALLOW_NEW_REFRESH_TOKENS_FOR_UNVERIFIED_USERS:
                    if user.is_active == False:
                        raise TokenError({"details": "User is inactive", "code": "user_inactive"})
                    
                if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]:
                    try:
                        refresh.blacklist()
                    except AttributeError:
                        pass
                
                # Creating new access tokens
                refresh.set_jti()
                refresh.set_exp()

                if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]:
                    OutstandingToken.objects.create(
                        user=user,
                        jti=payload[settings.SIMPLE_JWT["JTI_CLAIM"]],
                        token=str(refresh),
                        created_at=refresh.current_time,
                        expires_at=datetime_from_epoch(payload["exp"]),
                    )
                
                data["refresh"] = str(refresh)
            return data
        except TokenError as e:
            raise

        except serializers.ValidationError:
            raise

        except Exception:
            raise