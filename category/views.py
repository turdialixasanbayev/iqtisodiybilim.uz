from django.shortcuts import render
from django.views import View
from .models import Category
from article.models import Article


class CategoryPage(View):
    def get(self, request, slug):
        category = Category.objects.get(slug__exact=slug)
        articles = Article.objects.filter(category=category)
        latest_articles = Article.objects.order_by('-id')[:3]
        popular_articles = Article.objects.order_by('-views')[:3]
        context = {
            'articles': articles,
            'category': category,
            'latest_articles': latest_articles,
            'popular_articles': popular_articles
        }
        return render(request, 'categories.html', context=context)
