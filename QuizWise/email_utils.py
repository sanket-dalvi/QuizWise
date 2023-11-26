from django.core.mail import send_mail

def send_custom_email(subject, message, recipient_list):
    send_mail(subject, message, None, recipient_list, fail_silently=False)
