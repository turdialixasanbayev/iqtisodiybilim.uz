from django.urls import path
from .views import (
    ArticleDetailPage,
    ArticleListPage,
    HomePage,
    AboutPage
)


urlpatterns = [
    path('article-detail/<slug:slug>/', ArticleDetailPage.as_view(), name='article-detail'),
    path('articles/', ArticleListPage.as_view(), name='articles'),
    path('about/', AboutPage.as_view(), name='about'),
    path('', HomePage.as_view(), name='home'),
]
