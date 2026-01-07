from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Category
from article.models import Article


class CategoryPage(View):
    def get(self, request, slug):
        category = get_object_or_404(Category, slug__exact=slug)
        articles = Article.objects.filter(category=category).select_related('author', 'category').prefetch_related('tags')
        latest_articles = Article.objects.order_by('-created_at')[:3].select_related('category', 'author').prefetch_related('tags')
        popular_articles = Article.objects.order_by('-views')[:3].select_related('category', 'author').prefetch_related('tags')

        context = {
            'articles': articles,
            'category': category,
            'latest_articles': latest_articles,
            'popular_articles': popular_articles
        }

        return render(request, 'categories.html', context=context)
