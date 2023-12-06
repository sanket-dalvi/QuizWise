from .notification_strategy import NotificationStrategy
from QuizWise.email_utils import EmailSender

class EmailNotification(NotificationStrategy):
    """
    EmailNotification class extending NotificationStrategy for sending email notifications.
    """
    email_sender = EmailSender()

    def send_notification(self, user, quiz):
        """
        Sends an email notification to the user about the posted quiz.

        Args:
        - user (User): The user object to whom the email will be sent.
        - quiz (Quiz): The quiz object related to the notification.
        """
        self.email_sender.send_custom_email("QuizWise - Quiz Posted", f"", [user.email])
