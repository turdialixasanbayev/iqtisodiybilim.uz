from django.urls import path
from .views import (
    RegisterView,
    VerifyView,
    ProfileView,
    LogoutView,
    LoginView,
    ResendOTPView,
    UserDeleteView,
    ProfileUpdateView,
    PasswordUpdateView,
    UpdateEmailView,
    VerifyEmailUpdateView,
    ResendEmailUpdateOTPView,
    ForgotPasswordView,
    VerifyForgotPasswordView,
    ResendForgotPasswordOTPView,
    ResetPasswordView,
    )


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', ProfileView.as_view(), name='dashboard'),
    path('verify/', VerifyView.as_view(), name='verify'),
    path('verify/resend/', ResendOTPView.as_view(), name='resend-otp'),
    path('delete-account/', UserDeleteView.as_view(), name='delete-account'),
    path('profile-update/', ProfileUpdateView.as_view(), name='profile-update'),
    path("password-update/", PasswordUpdateView.as_view(), name="password-update"),
    path('email-update/', UpdateEmailView.as_view(), name='email-update'),
    path('email-update/verify/', VerifyEmailUpdateView.as_view(), name='verify-email-update'),
    path('email-update/resend/', ResendEmailUpdateOTPView.as_view(), name='resend-email-update-otp'),

    path(
        'forgot-password/',
        ForgotPasswordView.as_view(),
        name='forgot-password'
    ),

    path(
        'forgot-password/verify/',
        VerifyForgotPasswordView.as_view(),
        name='verify-forgot-password'
    ),

    path(
        'forgot-password/resend/',
        ResendForgotPasswordOTPView.as_view(),
        name='resend-forgot-password-otp'
    ),

    path(
        'forgot-password/reset/',
        ResetPasswordView.as_view(),
        name='reset-password'
    ),
]
