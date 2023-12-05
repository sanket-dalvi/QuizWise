from .notification_strategy import NotificationStrategy
from QuizCreator.models import Notification

class PortalNotification(NotificationStrategy):
    def send_notification(self, user, quiz):
        notification = f"A New Quiz {quiz.name} Has Been Posted"
        Notification.objects.create(user=user, quiz=quiz, notification=notification)