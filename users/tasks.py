from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


@shared_task
def send_verification_email(user_email, verify_url):
    subject = "Vérifiez votre adresse email - CamSecurePlot"
    from_email = settings.DEFAULT_FROM_EMAIL

    # Rendu du template HTML
    html_content = render_to_string("emails/verify_email.html", {"verify_url": verify_url})
    text_content = f"Cliquez pour vérifier votre compte: {verify_url}"

    msg = EmailMultiAlternatives(subject, text_content, from_email, [user_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
