from django.urls import path, include
from . import views

urlpatterns = [
    path('home', views.home, name="examinee_home"),
    path('examinee/view_quizzes', views.view_quizzes, name="view_quizzes"),
    path('examinee/take_quiz/<int:quiz_id>', views.take_quiz, name="take_quiz"),
    path('home/profile', views.profile, name="profile"),
    path('home/scores', views.scores, name="scores"),
    path('home/quiz_history', views.quiz_history, name="quiz_history"),
]