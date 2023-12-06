from django.core.mail import send_mail

class EmailSender:
    """
    Singleton class to send custom emails using Django's send_mail function.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation to ensure only one instance of EmailSender is created.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def send_custom_email(self, subject, message, recipient_list):
        """
        Sends a custom email using Django's send_mail function.

        Args:
        - subject (str): The subject of the email.
        - message (str): The message content of the email.
        - recipient_list (list): List of recipient email addresses.
        """
        send_mail(subject, message, None, recipient_list, fail_silently=False)
