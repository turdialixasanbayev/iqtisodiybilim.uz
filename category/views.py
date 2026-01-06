from django.shortcuts import render
from django.views import View
from .models import Category
from article.models import Article


class CategoryPage(View):
    def get(self, request, slug):
        category = Category.objects.get(slug__exact=slug)
        articles = Article.objects.filter(category=category)
        return render(request, 'category.html', context={'articles': articles})
