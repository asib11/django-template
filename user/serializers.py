from dataclasses import dataclass
from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.exceptions import AuthenticationFailed
from common.serializers import ResponseObj
from helpers.serializers import ContextMixin
from helpers.serializers import ExtendedImageField

from . import models as user_models
from .models import PasswordForgetOTP
from django.contrib.auth.password_validation import validate_password
from .tokens import email_verification_token_generator

class ProfileUpdateSerializer(serializers.ModelSerializer):
    image = ExtendedImageField()
    role = serializers.ChoiceField(choices=user_models.USER_ROLE.choices,required=False)
    class Meta:
        model = user_models.User
        fields = (
            'email',
            'first_name',
            'last_name',
            'image',
            'address1',
            'phone1',
            'role',
            'specialty',
            'years_of_experience',
            'hourly_rate',
            'all_agreements_accepted',
        )

    def validate(self, attrs):
        request = self.context.get('request')
        requested_role = attrs.get('role')

        if requested_role is None:
            return attrs

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError({'role': 'Authentication is required to change role.'})

        if request.user.role != user_models.USER_ROLE.SUPER_ADMIN and request.user.role != user_models.USER_ROLE.ADMIN:
            raise serializers.ValidationError({'role': 'Only super admin or admin can change roles.'})

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    image = ExtendedImageField()

    class Meta:
        model = user_models.User
        fields = (
            'email',
            'role',
            'first_name',
            'last_name',
            'image',
            'address1',
            'phone1',
            'specialty',
            'years_of_experience',
            'hourly_rate',
            'all_agreements_accepted',
        )


class OldPasswordChangeSerializer(serializers.Serializer, ContextMixin):
    _new_password: str

    password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_password(self, value):
        user = self.get_context_user()
        if not user.check_password(value):
            raise serializers.ValidationError('Wrong Password')
        return value

    def validate_new_password(self, value):
        self._new_password = value
        return value

    def validate_confirm_password(self, value):
        new_password = self._new_password
        if new_password != value:
            raise serializers.ValidationError('Password Missmatch')
        return value

    def create(self, validated_data):
        new_password = self._new_password
        user = self.get_context_user()
        user.set_password(new_password)
        user.save()
        return ResponseObj(
            details='Password Successfully Changed.'
        )



class TokenRefreshUserSerializer(TokenRefreshSerializer):
    user = UserProfileSerializer()


class UserEmailLoginSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField()

    def validate(self, attrs):
        try:
            data = super().validate(attrs)

        except AuthenticationFailed:
            email = attrs.get(self.username_field)
            user = user_models.User.objects.filter(email=email).first()

            if user is None:
                raise serializers.ValidationError('No user found with this email address.')

            if not user.is_active:
                raise serializers.ValidationError(
                    'Your account is not verified. Please check your email to verify your account.'
                )

            if not user.check_password(attrs.get('password')):
                raise serializers.ValidationError('Invalid password.')

            raise serializers.ValidationError('Unable to log in with provided credentials.')

        data['user'] = UserProfileSerializer(self.user).data
        return data



class UserRegisterSerializer(serializers.Serializer):
    @dataclass
    class Instance:
        user: AbstractUser


    _password: str = None

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=user_models.User.objects.all(),
            )
        ]
    )
    role = serializers.ChoiceField(choices=user_models.USER_ROLE.choices, default=user_models.USER_ROLE.USER)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    specialty = serializers.CharField(max_length=100, required=False)
    years_of_experience = serializers.IntegerField(min_value=0, required=False)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    all_agreements_accepted = serializers.BooleanField(default=False)


    def validate_password(self, value: str):
        self._password = value
        return value

    def validate_confirm_password(self, value: str):
        if self._password is None or self._password == value:
            return value
        raise serializers.ValidationError('Password Mismatch.')

    def create(self, validated_data: dict):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')

        for _ in range(5):
            user = user_models.User(**validated_data)
            user.is_staff = False
            user.is_active = False
            user.set_new_username()
            user.set_password(password)

            try:
                user.save()
                return self.Instance(user=user)
            except IntegrityError as exc:
                if 'user_user_username_key' not in str(exc):
                    raise

        raise serializers.ValidationError(
            'Unable to create a unique username at the moment. Please try again.'
        )


class EmailVerificationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        uid = attrs.get('uid')
        token = attrs.get('token')

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = user_models.User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, user_models.User.DoesNotExist):
            raise serializers.ValidationError('Invalid verification link.')

        if user.is_active:
            attrs['user'] = user
            attrs['already_verified'] = True
            return attrs

        if not email_verification_token_generator.check_token(user, token):
            raise serializers.ValidationError('Verification link is invalid or has expired.')

        attrs['user'] = user
        attrs['already_verified'] = False
        return attrs
    
class PasswordForgetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not user_models.User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class PasswordOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6, required=True, help_text="6-digit OTP sent to your email")

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only numbers.")
        return value

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = user_models.User.objects.get(email=email)
            otp_record = PasswordForgetOTP.objects.get(user=user, otp=otp, is_used=False)
        except (user_models.User.DoesNotExist, PasswordForgetOTP.DoesNotExist):
            raise serializers.ValidationError("Invalid email or OTP.")
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6, required=True, help_text="6-digit OTP sent to your email")
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Your new password"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm your new password"
    )

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only numbers.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        validate_password(attrs['new_password'])
        return attrs
