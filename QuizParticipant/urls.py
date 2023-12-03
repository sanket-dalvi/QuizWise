from django.urls import path, include
from . import views

urlpatterns = [
    path('home', views.home, name="examinee_home"),
    path('examinee/view_quizzes', views.view_quizzes, name="view_quizzes"),
    path('quiz/<int:quiz_id>/', views.view_quizzes, name='view_quiz'),
    path('examinee/take_quiz/<int:quiz_id>', views.take_quiz, name="take_quiz"),
    path('home/profile', views.profile, name="examinee_profile"),
    path('scores', views.scores, name="scores"),
    path('home/quiz_history', views.quiz_history, name="quiz_history"),
    path('examinee/submit_quiz/<int:quiz_id>', views.submit_quiz, name="submit_quiz"),
]