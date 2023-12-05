from django.db import models
from QuizCreator.models import Quiz, Question, User


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

class UserQuizStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    status = models.CharField(default="Active", max_length=10)
    timestamp = models.DateTimeField(auto_now=True)

    # Create a list to hold observers
    observers = []

    # Attach an observer to the list
    def attach_observer(self, observer):
        self.observers.append(observer)

    # Detach an observer from the list
    def detach_observer(self, observer):
        self.observers.remove(observer)

    # Notify all observers
    def notify_observers(self):
        for observer in self.observers:
            observer.notify(self)

    def save(self, *args, **kwargs):
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