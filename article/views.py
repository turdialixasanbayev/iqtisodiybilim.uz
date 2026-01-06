from django.shortcuts import render
from django.views import View
from .models import Article
from user.models import Agent


class ArticleDetailPage(View):
    def get(self, request, slug):
        article = Article.objects.get(slug__exact=slug)
        context = {
            'article': article
        }
        return render(request, 'article-detail.html', context)

class ArticleListPage(View):
    def get(self, request):
        return render(request, 'articles.html')

class HomePage(View):
    def get(self, request):
        latest = Article.objects.order_by('-id')[:3]
        popular = Article.objects.order_by('-views')[:3]
        context = {'latest': latest, 'popular': popular}
        return render(request, 'home.html', context)

class AboutPage(View):
    def get(self, request):
        agents = Agent.objects.all()[:3]
        return render(request, 'about.html', {"agents": agents})
