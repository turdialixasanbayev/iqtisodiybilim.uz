from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
import random
from django.conf import settings
from django.utils import timezone


class CustomUser(AbstractUser):
    # groups = None
    # user_permissions = None
    username = None
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to='profile_images', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email


class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    @staticmethod
    def generate():
        return str(random.randint(100000, 999999))

    class Meta:
        verbose_name = "EmailOTP"
        verbose_name_plural = "EmailOTP"

    def __str__(self):
        return self.user.email


class Agent(models.Model):
    full_name = models.CharField(max_length=200)
    job = models.CharField(max_length=200)
    image = models.ImageField(upload_to='agents', null=True, blank=True)

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return self.full_name
