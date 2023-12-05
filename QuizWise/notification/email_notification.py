from .notification_strategy import NotificationStrategy
from QuizWise.email_utils import EmailSender

class EmailNotification(NotificationStrategy):
    email_sender = EmailSender()
    def send_notification(self, user, quiz):
        self.email_sender.send_custom_email("QuizWise - Quiz Posted", f"", [user.email])
