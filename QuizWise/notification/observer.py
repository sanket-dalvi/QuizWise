from abc import ABC, abstractmethod

class Observer(ABC):

    @abstractmethod
    def notify(self, user_quiz_status):
        pass