from django.urls import path
from .views import (
    RegisterView,
    ProfileView,
    LogoutView,
    LoginView,
    UserDeleteView,
    ProfileUpdateView,
    PasswordUpdateView,
    )


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', ProfileView.as_view(), name='dashboard'),
    path('delete-account/', UserDeleteView.as_view(), name='delete-account'),
    path('profile-update/', ProfileUpdateView.as_view(), name='profile-update'),
    path("password-update/", PasswordUpdateView.as_view(), name="password-update"),
]
