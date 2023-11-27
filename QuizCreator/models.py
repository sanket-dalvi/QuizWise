from django.db import models
from QuizWise.models import User


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    visible_to_others = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class QuestionType(models.Model):
    type_code = models.CharField(max_length=3, unique=True)
    type_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type_name} ({self.type_code})"

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField()
    type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    answer = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='modified_questions')
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Question: {self.question[:50]}"

