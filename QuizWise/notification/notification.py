from .observer import Observer
from .email_notification import EmailNotification
from .mobile_notifcation import MobileNotification

class Notification(Observer):

    def notify(self, user_quiz_status):
        user = user_quiz_status.user
        quiz = user_quiz_status.quiz
        print("Notified")
        if user.email_notification:
            email_notification = EmailNotification()
            email_notification.send_notification(user, quiz)

        if user.mobile_notification:
            mobile_notification = MobileNotification()
            email_notification.send_notification(user, quiz)
        