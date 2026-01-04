from django.urls import path

from .views import CategoryPage


urlpatterns = [
    path('category/', CategoryPage.as_view(), name='category'),
]
