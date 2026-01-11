from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Article(models.Model):
    title = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=300, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE, related_name='article_author')
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE, related_name='article_category')
    tags = models.ManyToManyField('category.Tag', blank=True, related_name='article_tags')
    views = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    reading_time = models.PositiveSmallIntegerField(null=True, blank=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def get_absolute_url(self, *args, **kwargs):
        return reverse('article-detail', kwargs={'slug': self.slug})

    @property
    def average_rate(self):
        avg = self.comment_article.aggregate(avg=Avg("rate"))["avg"]
        return round(avg, 1) if avg else 0

    @property
    def rate_count(self):
        return self.comment_article.count()
    
    @property
    def comment_count(self):
        return self.comment_article.count()


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comment_article')
    user = models.ForeignKey('user.CustomUser', on_delete=models.SET_NULL, null=True, related_name='comment_user')
    rate = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        null=True,
        blank=True
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_email = self.user.email if self.user else "Deleted User"
        return f"{user_email} --> {self.article.title}"

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
