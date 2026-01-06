from django.db import models


class Contact(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return self.full_name
