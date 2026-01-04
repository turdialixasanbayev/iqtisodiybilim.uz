from django.shortcuts import render
from django.views import View


class ArticleDetailPage(View):
    def get(self, request):
        return render(request, 'article-detail.html')

class ArticleListPage(View):
    def get(self, request):
        return render(request, 'articles.html')

class HomePage(View):
    def get(self, request):
        return render(request, 'home.html')

class AboutPage(View):
    def get(self, request):
        return render(request, 'about.html')
