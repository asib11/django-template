from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    path('auth/profile/update/', views.UserProfileUpdateAPIView.as_view()),
    path('auth/profile/', views.UserProfileAPIView.as_view()),
    path('auth/login/email/', views.UserEmailLoginAPIView.as_view()),
    # path('auth/login/', views.UserLoginAPIView.as_view()),
    path('auth/register/', views.UserRegisterAPIView.as_view()),
    path('auth/verify-email/', views.EmailVerificationAPIView.as_view(), name='email-verify'),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/password/forgot/', views.PasswordForgetRequestView.as_view(), name='forgot-password'),
    path('auth/password/verify/', views.PasswordOTPVerifyView.as_view(), name='reset-password'),
    path('auth/password/reset/', views.PasswordResetConfirmView.as_view(), name='reset-password'),
    path('auth/password/change/old/', views.OldPasswordChangeAPIView.as_view()),
]

