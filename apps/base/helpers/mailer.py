from django.conf import settings
from django.core.mail import send_mail


def send_mail_helper(title, body):
    send_mail(
        title,
        body,
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
