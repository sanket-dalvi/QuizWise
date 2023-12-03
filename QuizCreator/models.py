from django.db import models
from QuizWise.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver


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
    
@receiver(post_migrate)
def add_initial_question_types(sender, **kwargs):
    if sender.name == 'QuizCreator':  
        QuestionType.objects.get_or_create(
            type_code='RB', defaults={'type_name': 'Radio Button - Multiple Options With One Answer'}
        )
        QuestionType.objects.get_or_create(
            type_code='CB', defaults={'type_name': 'Checkbox - Multiple Options With One or More Answers'}
        )
        QuestionType.objects.get_or_create(
            type_code='FT', defaults={'type_name': 'Free Text Answer'}
        )

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


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option = models.CharField(max_length=255)


class CategoryQuestionMap(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField()
    total_questions = models.IntegerField()
    passcode =  models.CharField(max_length=15, default="UnLockMe")
    visible = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quiz')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='modified_quiz')
    modified_at = models.DateTimeField(auto_now=True)
 
class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class Groups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    total_students = models.IntegerField()

class GroupExamineeMapping(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)