from abc import ABC, abstractmethod

class NotificationStrategy(ABC):
    @abstractmethod
    def send_notification(self, user, quiz):
        pass
    