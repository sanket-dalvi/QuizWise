from django.db import models
from QuizCreator.models import Quiz, Question, User


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

class UserQuizStatus(models.Model):
    """
    Model representing the status of a user's interaction with a quiz.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    status = models.CharField(default="Active", max_length=10)
    timestamp = models.DateTimeField(auto_now=True)

    # Create a list to hold observers
    observers = []

    def attach_observer(self, observer):
        """
        Attach an observer to the list of observers.

        Args:
        - observer (Observer): The observer object to be attached.
        """
        self.observers.append(observer)

    def detach_observer(self, observer):
        """
        Detach an observer from the list of observers.

        Args:
        - observer (Observer): The observer object to be detached.
        """
        self.observers.remove(observer)

    def notify_observers(self):
        """Notify all attached observers."""
        for observer in self.observers:
            observer.notify(self)

    def save(self, *args, **kwargs):
        """
        Save method override to notify observers upon saving the instance.
        """
        is_new = not self.pk  # Check if it's a new instance
        super().save(*args, **kwargs)
        if is_new:
            self.notify_observers()



class UserQuizScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)