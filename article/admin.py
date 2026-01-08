from django.contrib import admin
from .models import Article, Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'views',
        'average_rate',
        'rate_count',
        'comment_count',
        'published_at',
        "created_at",
        'updated_at',
    )
    search_fields = ('title',)
    prepopulated_fields = {'slug': ("title",)}
    list_filter = ('author',)
    filter_horizontal = ('tags',)
    autocomplete_fields = ('author', 'category',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'article__title', 'user__email', 'rate', 'created_at', 'updated_at')
    search_fields = ('article__title', 'user__email', 'rate',)
    autocomplete_fields = ('user', 'article',)
    list_filter = ('rate',)
