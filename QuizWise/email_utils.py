from django.core.mail import send_mail

class EmailSender:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def send_custom_email(self, subject, message, recipient_list):
        send_mail(subject, message, None, recipient_list, fail_silently=False)
