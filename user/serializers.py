from dataclasses import dataclass
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from common.serializers import ResponseObj
from helpers.serializers import ContextMixin
from helpers.serializers import ExtendedImageField

from . import models as user_models
from .models import PasswordForgetOTP
from django.contrib.auth.password_validation import validate_password

class ProfileUpdateSerializer(serializers.ModelSerializer):
    image = ExtendedImageField()

    class Meta:
        model = user_models.User
        fields = (
            'email',
            'first_name',
            'last_name',
            'image',
            'address1',
            'address2',
            'phone1',
            'phone2',
        )


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
            'designation',
            'address1',
            'address2',
            'phone1',
            'phone2',
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
        data = super().validate(attrs)
        data['user'] = UserProfileSerializer(self.user).data
        return data



class UserRegisterSerializer(serializers.Serializer):
    @dataclass
    class Instance:
        user: AbstractUser
        token: RefreshToken

        @classmethod
        def from_user(cls, password: str, **validated_data: dict):
            user = user_models.User(**validated_data)
            user.is_staff = False
            user.is_active = True
            user.set_new_username()
            user.set_password(password)
            user.save()
            user_models.School.objects.create(
                user=user,
                name="",
            )

            token = RefreshToken.for_user(user=user)

            instance = cls(user=user, token=token)
            return instance

        @property
        def refresh(self):
            return str(self.token)

        @property
        def access(self):
            return str(self.token.access_token)


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
    password = serializers.CharField()
    confirm_password = serializers.CharField()


    def validate_password(self, value: str):
        self._password = value
        return value

    def validate_confirm_password(self, value: str):
        if self._password is None or self._password == value:
            return value
        raise serializers.ValidationError('Password Mismatch.')

    def create(self, validated_data: dict):
        validated_data.pop('confirm_password')
        instance = self.Instance.from_user(**validated_data)
        return instance
    
class PasswordForgetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not user_models.User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class PasswordOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=4, max_length=4, required=True, help_text="4-digit OTP sent to your email")

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
    otp = serializers.CharField(min_length=4, max_length=4, required=True, help_text="4-digit OTP sent to your email")
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