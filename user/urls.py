from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    path('v1/auth/profile/update/', views.UserProfileUpdateAPIView.as_view()),
    path('v1/auth/profile/', views.UserProfileAPIView.as_view()),
    path('v1/auth/login/email/', views.UserEmailLoginAPIView.as_view()),
    # path('v1/auth/login/', views.UserLoginAPIView.as_view()),
    path('v1/auth/register/', views.UserRegisterAPIView.as_view()),
    path('v1/auth/refresh/', TokenRefreshView.as_view()),
    path('v1/auth/password/forgot/', views.PasswordForgetRequestView.as_view(), name='forgot-password'),
    path('v1/auth/password/verify/', views.PasswordOTPVerifyView.as_view(), name='reset-password'),
    path('v1/auth/password/reset/', views.PasswordResetConfirmView.as_view(), name='reset-password'),
    path('v1/auth/password/change/old/', views.OldPasswordChangeAPIView.as_view()),
]

