# Rest-Framework Import
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_yasg.utils import swagger_auto_schema

# Django Import
from django.shortcuts import render
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import check_password

# Project Level Imports
from common.helpers import validation_error_handler
from authentication.models import User
from .helpers import AuthHelper
from .tokens import account_activation_token
# from common.utils import Utility
from .serializers import CreateUserSerializer, CustomTokenRefreshSerializer, UserLoginSerializer, LogoutRequestSerializer
import logging
from .tasks import send_verify_email_link

logger = logging.getLogger(__file__)

# Create your views here.
class SignUpView(GenericAPIView):

    # DRF uses this variable to display the deafult html template
    serializer_class = CreateUserSerializer

    @swagger_auto_schema(responses={status.HTTP_200_OK: CreateUserSerializer})
    def post(self, request, *args, **kwargs):
        request_data = request.data
        # data is required - otherwise it will not perform validations
        serializer = self.serializer_class(data=request_data)

        if serializer.is_valid() is False:
            return Response({
                "status": "error",
                "message": validation_error_handler(serializer.errors), # For the toast
                "payload": {
                    "errors": serializer.errors
                }
            }, status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        email = validated_data['email']
        password = validated_data['password']

        # If verification fails because of third-party apps, user can again signup again
        existing_user = User.objects.filter(email=email).first()

        if existing_user is not None:
            if existing_user.is_active is False:
                existing_user.set_password(password)
                existing_user.save()
                user = existing_user
            else:
                return Response({
                    "stautus": "error",
                    "message": "Account with this email address already exists.",
                    "payload": {},
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            username = AuthHelper.create_username(email=email)
            user = User.objects.create_user(
                username = username,
                is_active = False,
                **validated_data
            )
        
        serializer_data = self.serializer_class(user).data

        """
        We are sending emails via Celery in background.
        """

        # send email
        # subject = "Verify Email for your Account Verification on WonderShop"
        # template = "auth/email/verify_email.html"
        # context_data = {
        #     "host": settings.FRONTEND_HOST,
        #     "uid": urlsafe_base64_encode(force_bytes(user.id)),
        #     "token": account_activation_token.make_token(user=user),
        #     "protocol": settings.FRONTEND_PROTOCOL
        # }

        # print(context_data)
        # try:
        #     # Utility.send_mail_via_sendgrid(
        #     #     user.email,
        #     #     subject,
        #     #     template,
        #     #     context_data
        #     # )
        #     return Response({
        #         "status": "success",
        #         "message": "Sent the account verification link to your email address",
        #         "payload": {
        #             **serializer_data,
        #             "tokens": AuthHelper.get_tokens_for_user(user) # For log in purpose, If the email is the verified this token will not work.
        #         }
        #     })
        # except Exception:
        #     logger.error("Some error occurred in signup endpoint", exc_info=True)
        #     return Response({
        #         "status": "error",
        #         "message": "Some error occurred",
        #         "payload": {}
        #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        send_verify_email_link.delay(user)
        return Response({
            "status": "success",
            "message": "Sent the account verification link to your email address",
            "payload": {
                **serializer_data,
                "tokens": AuthHelper.get_tokens_for_user(user)
            }
        })

class ActivateAccountView(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            return Response({
                'status': 'success',
                'message': 'account verified',
                'payload': {},
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Activation link is invalid",
            "payload": {}
        }, status=status.HTTP_403_FORBIDDEN)


class LoginView(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid() is False:
            return Response({
                "status": "error",
                "message": validation_error_handler(serializer.errors),
                "payload": {
                    "errors": serializer.errors
                }
            }, status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        username_or_email = validated_data["username_or_email"]
        password = validated_data["password"]
        user = (
            User.objects.filter(email=username_or_email).first()
            or
            User.objects.filter(username=username_or_email).first()
        )
        if user is not None:
            validate_password = check_password(
                password, user.password
            )
            if validate_password:
                if user.is_active is False:
                    return Response({
                        "status": "error",
                        "message": "User account is not active. Please verify your email first.",
                        "payload": {}
                    }, status=status.HTTP_403_FORBIDDEN)
                serializer_data = self.serializer_class(
                    user, context={"request": request}
                )
                return Response({
                    "status": "success",
                    "message": "Login Successful",
                    "payload": {
                        **serializer_data.data,
                        "token": AuthHelper.get_tokens_for_user(user)
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "message": "Invalid Credentials",
                    "payload": {}
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status": "error",
                "message": "No user found",
                "payload": {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)

class UserLogoutView(GenericAPIView):
    serializer_class = LogoutRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)

        if serializer.is_valid() is False:
            return Response({
                "status": "error",
                "message": validation_error_handler(serializer.errors),
                "payload": {
                    "errors": serializer.errors
                }
            }, status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data

        try:
            if validated_data.get("all"):
                for token in OutstandingToken.objects.filter(user=request.user):
                    _, _ = BlacklistedToken.objects.get_or_create(token=token) # Returns object and True if the token is present, else False
                return Response({
                    "status": "success",
                    "message": "Successfully logged out from all devices",
                    "payload": {}
                }, status=status.HTTP_200_OK)
            
            refresh_token = validated_data.get("refresh")

            # Create a RefreshToken Object to block the token
            token = RefreshToken(token=refresh_token)
            token.blacklist()

            return Response({
                "status": "success",
                "message": "Successfully logged out",
                "payload": {}
            }, status=status.HTTP_200_OK)
        
        except TokenError:
            return Response({
                "detail": "Token is blacklisted",
                "code": "token_not_valid"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception:
            return Response({
                "status": "error",
                "message": "Error occurred",
                "payload": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)