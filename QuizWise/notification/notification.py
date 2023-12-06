from .observer import Observer
from .email_notification import EmailNotification
from .mobile_notification import MobileNotification
from .portal_notification import PortalNotification

class Notification(Observer):
    """
    Notification class extending Observer to implement notifications.
    """

    def notify(self, user_quiz_status):
        """
        Notify method to send notifications to users based on their preferences.

        Args:
        - user_quiz_status (UserQuizStatus): Object containing user and quiz status.
        """

        user = user_quiz_status.user
        quiz = user_quiz_status.quiz

        # Initialize notification strategy based on user preferences
        if user.email_notification:
            self.notification_strategy = EmailNotification()
            self.notification_strategy.send_notification(user, quiz)

        if user.mobile_notification:
            self.notification_strategy = MobileNotification()
            self.notification_strategy.send_notification(user, quiz)

        # Send portal notification (default strategy)
        self.notification_strategy = PortalNotification()
        self.notification_strategy.send_notification(user, quiz)
