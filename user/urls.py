from django.urls import path
from .views import (
    RegisterView,
    VerifyView,
    ProfileView,
    LogoutView,
    LoginView,
    ResendOTPView,
    )


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', ProfileView.as_view(), name='dashboard'),
    path('verify/', VerifyView.as_view(), name='verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/resend/', ResendOTPView.as_view(), name='resend-otp'),
]
