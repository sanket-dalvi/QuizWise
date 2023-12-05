from .notification_strategy import NotificationStrategy
from QuizWise.models import Notification

class PortalNotification(NotificationStrategy):
    def send_notification(self, user, quiz):
        notification = f""
        Notification.objects.create(user=user, quiz=quiz, notification=notification)