from .notification_strategy import NotificationStrategy
from QuizCreator.models import Notification

class PortalNotification(NotificationStrategy):
    """
    PortalNotification class extending NotificationStrategy for portal notifications.
    """
    def send_notification(self, user, quiz):
        """
        Creates a portal notification for the user regarding the posted quiz.

        Args:
        - user (User): The user object to whom the portal notification will be associated.
        - quiz (Quiz): The quiz object related to the notification.
        """
        notification = f"A New Quiz {quiz.name} Has Been Posted"
        Notification.objects.create(user=user, quiz=quiz, notification=notification)
