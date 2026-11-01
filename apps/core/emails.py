from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_templated_email(subject, template, context, to, reply_to=None):
    message = EmailMultiAlternatives(
        subject=" ".join(str(subject).split()),  # never allow newlines in headers
        body=render_to_string(f"emails/{template}.txt", context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        reply_to=reply_to or [],
    )
    message.attach_alternative(render_to_string(f"emails/{template}.html", context), "text/html")
    message.send()
