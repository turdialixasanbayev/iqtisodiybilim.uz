from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Article, Comment
from user.models import Agent
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ArticleDetailPage(View):
    def get(self, request, slug):
        article = get_object_or_404(Article, slug__exact=slug)
        related_articles = Article.objects.filter(category=article.category).exclude(id=article.id)
        comments = Comment.objects.filter(article=article).select_related('user', 'article').order_by('-created_at')

        article.views += 1
        article.last_viewed_at = timezone.now()
        article.save(update_fields=["views", "last_viewed_at"])

        context = {
            'article': article,
            'related_articles': related_articles,
            'comments': comments,
        }

        return render(request, 'article-detail.html', context)
    
    @method_decorator(login_required)
    def post(self, request, slug):
        article = get_object_or_404(Article, slug__exact=slug)

        rate = request.POST.get('rate')
        comment = request.POST.get('comment')

        Comment.objects.create(article=article, user=request.user, comment=comment, rate=rate)
        messages.success(request, "Your comment has been posted successfully")

        return redirect(article.get_absolute_url())

class ArticleListPage(View):
    def get(self, request):
        articles = Article.objects.order_by('-id')
        return render(request, 'articles.html', context={'articles': articles})

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
