from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

class Command(BaseCommand):
    help = "Create superuser if not exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = env("DJANGO_SUPERUSER_EMAIL")
        password = env("DJANGO_SUPERUSER_PASSWORD")

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{email}' created!"))
        else:
            self.stdout.write(self.style.NOTICE(f"Superuser '{email}' already exists"))
