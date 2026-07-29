import logging
import random

from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from common.serializers import ResponseSerializer
from helpers.api_view import create_view
from helpers.response import error_response, response
from projectile import env

from . import models as user_models
from . import serializers as user_serializers
from .email_utils import build_email_verification_link, send_verification_email, send_welcome_email


logger = logging.getLogger(__name__)



class UserRegisterAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializers.UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as exc:
            return error_response(
                details=exc.detail,
                code="REGISTER_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                instance = serializer.save()
                user = instance.user
                verification_link = build_email_verification_link(user=user, request=request)
                send_verification_email(user=user, verification_link=verification_link)
        except Exception:
            logger.exception(
                "Failed to register user and send verification email for email=%s",
                request.data.get("email"),
            )
            return error_response(
                details="Registration failed. Could not send verification email. Please try again.",
                code="REGISTER_FAILED",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return response(
            details="Registration successful. Verification email has been sent.",
            code="REGISTER_SUCCESS",
            status_code=status.HTTP_201_CREATED,
        )


class EmailVerificationAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializers.EmailVerificationSerializer
    FRONTEND_LOGIN_URL = env.FRONTEND_LOGIN_URL 

    def _verify(self, data):
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as exc:
            error_message = exc.detail
            if isinstance(error_message, dict):
                error_message = list(error_message.values())[0]
            if isinstance(error_message, list):
                error_message = error_message[0]
            return None, str(error_message)

        user = serializer.validated_data['user']
        already_verified = serializer.validated_data.get('already_verified', False)

        if already_verified:
            return user, None

        user.is_active = True
        user.save(update_fields=['is_active'])

        try:
            send_welcome_email(user=user)
        except Exception:
            logger.exception(
                'Failed to send welcome email after account activation for user_id=%s',
                user.pk,
            )

        return user, None

    def get(self, request, *args, **kwargs):
        user, error_message = self._verify(
            data={
                'uid': request.query_params.get('uid'),
                'token': request.query_params.get('token'),
            }
        )

        if error_message:
            return render(
                request,
                'email_verification_result.html',
                {
                    'success': False,
                    'message': error_message,
                    'redirect_url': self.FRONTEND_LOGIN_URL,
                },
            )

        return render(
            request,
            'email_verification_result.html',
            {
                'success': True,
                'message': 'Your email has been verified successfully!',
                'redirect_url': self.FRONTEND_LOGIN_URL,
            },
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as exc:
            return error_response(
                details=exc.detail,
                code="EMAIL_VERIFICATION_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data['user']
        already_verified = serializer.validated_data.get('already_verified', False)

        if not already_verified:
            user.is_active = True
            user.save(update_fields=['is_active'])
            try:
                send_welcome_email(user=user)
            except Exception:
                logger.exception(
                    'Failed to send welcome email after account activation for user_id=%s',
                    user.pk,
                )

        refresh = RefreshToken.for_user(user)
        user_data = user_serializers.UserProfileSerializer(
            user,
            context=self.get_serializer_context(),
        ).data

        return response(
            details='Email verified successfully.' if not already_verified else 'Email already verified.',
            code='EMAIL_VERIFICATION_SUCCESS',
            status_code=status.HTTP_200_OK,
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data,
            },
        )


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
        except serializers.ValidationError as e:
            return error_response(
                details=e.detail,
                code="LOGIN_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

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
            code="PROFILE_RETRIEVE_SUCCESS",
            status_code=status.HTTP_200_OK,
            data=serializer.data
        )


@create_view(
    request_body=user_serializers.OldPasswordChangeSerializer,
    response=ResponseSerializer,
)
class OldPasswordChangeAPIView(generics.CreateAPIView):
    serializer_class = user_serializers.OldPasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return error_response(
                details=e.detail,
                code="PASSWORD_CHANGE_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return response(
            details="Password changed successfully",
            code="PASSWORD_CHANGE_SUCCESS",
            status_code=status.HTTP_200_OK
        )


class UserProfileUpdateAPIView(generics.UpdateAPIView):
    serializer_class = user_serializers.ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return error_response(
                details=e.detail,
                code="PROFILE_UPDATE_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        self.perform_update(serializer)
        return response(
            details="Profile updated successfully",
            code="PROFILE_UPDATE_SUCCESS",
            status_code=status.HTTP_200_OK,
            data=serializer.data
        )



class PasswordForgetRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializers.PasswordForgetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return error_response(
                details=e.detail,
                code="PASSWORD_FORGET_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

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
        otp = str(random.randint(100000, 999999))
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
                code="OTP_SEND_SUCCESS",
                status_code=status.HTTP_200_OK
            )
        except Exception:
            logger.exception(
                "Failed to send password reset OTP email for email=%s",
                email,
            )
            return error_response(
                details="Failed to send OTP email. Please try again.",
                code="EMAIL_SEND_FAILED",
                status_code=500
            )


class PasswordOTPVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializers.PasswordOTPVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return error_response(
                details=e.detail,
                code="OTP_VERIFY_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = user_models.User.objects.get(email=email)
        except user_models.User.DoesNotExist:
            return error_response(
                details="User not found.",
                code="USER_NOT_FOUND",
                status_code=404
            )

        otp_obj = user_models.PasswordForgetOTP.objects.filter(
            user=user, otp=otp, is_used=False
        ).order_by("-created_at").first()

        if not otp_obj:
            return error_response(
                details="Invalid OTP.",
                code="INVALID_OTP",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            otp_obj.is_used = True
            otp_obj.save()
            return error_response(
                details="OTP has expired.",
                code="OTP_EXPIRED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return response(
            details="OTP is valid.",
            code="OTP_VERIFY_SUCCESS",
            status_code=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializers.PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return error_response(
                details=e.detail,
                code="PASSWORD_RESET_FAILED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

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

        otp_obj = user_models.PasswordForgetOTP.objects.filter(
            user=user, otp=otp, is_used=False
        ).order_by('-created_at').first()

        if not otp_obj:
            return error_response(
                details="Invalid OTP or OTP already used.",
                code="INVALID_OTP",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            otp_obj.is_used = True
            otp_obj.save()
            return error_response(
                details="OTP has expired. Please request a new one.",
                code="OTP_EXPIRED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        otp_obj.is_used = True
        otp_obj.save()

        return response(
            details="Password has been reset successfully.",
            code="PASSWORD_RESET_SUCCESS",
            status_code=status.HTTP_200_OK,
            data={'email': user.email}
        )
