from django.urls import path

from .views import (
    RegisterView,
    ProfileView,
    LogoutView,
    LoginView,
    DeleteAccountView,
    )


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', ProfileView.as_view(), name='dashboard'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]
