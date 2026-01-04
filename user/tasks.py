from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 10})
def send_notification_email_task(self, to, subject, message):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to],
        fail_silently=False
    )
    return f"Email sent to {to}"
