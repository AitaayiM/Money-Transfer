from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_verification_email(email, code):
    send_mail(
        'Verification Code',
        f'Your verification code is: {code}',
        'noreply@moneytransfer.com',
        [email],
        fail_silently=False,
    )

@shared_task
def send_reset_password_email(email, link):
    send_mail(
        "Password reset from M-Read",
        f"Your password reset link is: {link}",
        "noreply@moneytransfer.com",
        [email],
    )
