from django.urls import path, include
from . import views

urlpatterns = [
    path('home', views.home, name="examinee_home"),
    path('home/profile', views.profile, name="profile"),
    path('home/scores', views.scores, name="scores"),
    path('home/quiz_history', views.quiz_history, name="quiz_history"),
]