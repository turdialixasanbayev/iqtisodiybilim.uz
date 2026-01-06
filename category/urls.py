from django.urls import path

from .views import CategoryPage


urlpatterns = [
    path('categories/<slug:slug>/', CategoryPage.as_view(), name='categories'),
]
