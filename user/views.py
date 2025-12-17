from rest_framework import generics
from django.db import models as dj_models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.views import APIView
from helpers.response import response, error_response
from helpers.api_view import create_view
from common.serializers import ResponseSerializer
from helpers.response import response, error_response

from . import serializers as user_serializers
from . import models as user_models
from .permissions import IsAdminUser, IsActiveUser

import random



@create_view(
    request_body=user_serializers.UserRegisterSerializer,
    response=TokenRefreshSerializer
)
class UserRegisterAPIView(generics.CreateAPIView):
    permission_classes = []
    queryset = user_models.User.objects.all()


@create_view(
    request_body=TokenObtainPairSerializer,
    response=TokenRefreshSerializer
)
class UserLoginAPIView(TokenObtainPairView):
    pass


@create_view(
    request_body=user_serializers.UserEmailLoginSerializer,
    response=user_serializers.TokenRefreshUserSerializer
)
class UserEmailLoginAPIView(TokenObtainPairView):
    serializer_class = user_serializers.UserEmailLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            return response(
                details="Login successful",
                code="LOGIN_SUCCESS",
                status_code=status.HTTP_200_OK,
                data={
                    'refresh': serializer.validated_data['refresh'],
                    'access': serializer.validated_data['access'],
                    'user': serializer.validated_data['user']
                }
            )
        except serializers.ValidationError as e:
            return error_response(
                details=str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail),
                code="LOGIN_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST
            )



class UserProfileAPIView(generics.RetrieveAPIView):
    serializer_class = user_serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response(
            details="Profile retrieved successfully",
            code="PROFILE_RETRIEVED",
            data=serializer.data
        )
    

@create_view(
    request_body=user_serializers.OldPasswordChangeSerializer,
    response=ResponseSerializer,
)
class OldPasswordChangeAPIView(generics.CreateAPIView):
    pass


class UserProfileUpdateAPIView(generics.UpdateAPIView):
    serializer_class = user_serializers.ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)
        
    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return response(
                details="Profile updated successfully",
                code="PROFILE_UPDATED",
                data=serializer.data
            )
        except Exception as e:
            return error_response(
                details=str(e),
                code="UPDATE_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST
            )



class PasswordForgetRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializers.PasswordForgetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = user_models.User.objects.get(email=email)
        except user_models.User.DoesNotExist:
            return error_response(
                details="User with this email does not exist.",
                code="USER_NOT_FOUND",
                status_code=404
            )

        user_models.PasswordForgetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
        otp = str(random.randint(1000, 9999))
        user_models.PasswordForgetOTP.objects.create(user=user, otp=otp)

        html_message = render_to_string(
            'password_reset_otp.html',
            {'otp': otp, 'year': timezone.now().year, 'user': user}
        )

        try:
            send_mail(
                subject='Password Reset OTP',
                message=f'Your OTP for password reset is: {otp}',
                from_email=env.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message
            )
            return response(
                details="OTP has been sent to your email.",
                code="OTP_SENT"
            )
        except Exception:
            return error_response(
                details="Failed to send OTP email. Please try again.",
                code="EMAIL_SEND_FAILED",
                status_code=500
            )


class PasswordOTPVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializers.PasswordOTPVerifySerializer

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return error_response(
                details="Email and OTP are required.",
                code="MISSING_FIELDS"
            )

        try:
            user = user_models.User.objects.get(email=email)
        except user_models.User.DoesNotExist:
            return error_response(
                details="User not found.",
                code="USER_NOT_FOUND",
                status_code=404
            )

        otp_obj = user_serializers.PasswordForgetOTP.objects.filter(user=user, otp=otp, is_used=False).order_by("-created_at").first()

        if not otp_obj:
            return error_response(
                details="Invalid OTP.",
                code="INVALID_OTP"
            )

        if otp_obj.is_expired():
            otp_obj.is_used = True
            otp_obj.save()
            return error_response(
                details="OTP has expired.",
                code="OTP_EXPIRED"
            )

        return response(
            details="OTP is valid.",
            code="OTP_VALID"
        )

class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializers.PasswordResetConfirmSerializer

    def post(self, request):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = user_models.User.objects.get(email=email)
        except user_models.User.DoesNotExist:
            return error_response(
                details="User not found.",
                code="USER_NOT_FOUND",
                status_code=404
            )

        otp_obj = user_models.PasswordForgetOTP.objects.filter(user=user, otp=otp, is_used=False).order_by('-created_at').first()

        if not otp_obj:
            return error_response(
                details="Invalid OTP or OTP already used.",
                code="INVALID_OTP"
            )

        if otp_obj.is_expired():
            otp_obj.is_used = True
            otp_obj.save()
            return error_response(
                details="OTP has expired. Please request a new one.",
                code="OTP_EXPIRED"
            )

        user.set_password(new_password)
        user.save()
        otp_obj.is_used = True
        otp_obj.save()

        return response(
            details="Password has been reset successfully.",
            code="PASSWORD_RESET_SUCCESS",
            data={'email': user.email}
        )