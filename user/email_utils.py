from urllib.parse import urlencode

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from projectile import env

from .tokens import email_verification_token_generator


def build_email_verification_link(user, request=None):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token_generator.make_token(user)

    verify_path = reverse('email-verify')
    query = urlencode({'uid': uid, 'token': token})

    if request is not None:
        return request.build_absolute_uri(f'{verify_path}?{query}')

    base_url = (env.SWAGGER_DEFAULT_API_URL or '').rstrip('/')
    if base_url:
        return f'{base_url}{verify_path}?{query}'

    return f'{verify_path}?{query}'


def send_verification_email(user, verification_link):
    display_name = user.get_full_name().strip() or user.username or 'there'

    html_message = render_to_string(
        'email_verification.html',
        {
            'user': user,
            'display_name': display_name,
            'verification_link': verification_link,
            'project_name': env.PROJECT_NAME,
            'year': timezone.now().year,
        },
    )

    send_mail(
        subject=f'Verify your {env.PROJECT_NAME} account',
        message=(
            f'Hi {display_name}, please verify your account by clicking this link: '
            f'{verification_link}'
        ),
        from_email=env.EMAIL_HOST_USER,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_welcome_email(user):
    display_name = user.get_full_name().strip() or user.username or 'there'

    html_message = render_to_string(
        'welcome_email.html',
        {
            'user': user,
            'project_name': env.PROJECT_NAME,
            'year': timezone.now().year,
        },
    )

    send_mail(
        subject=f'Welcome to {env.PROJECT_NAME}',
        message=f'Hi {display_name}, welcome to {env.PROJECT_NAME}.',
        from_email=env.EMAIL_HOST_USER,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
