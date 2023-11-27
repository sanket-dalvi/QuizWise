from django.urls import path, include
from . import views

urlpatterns = [
    path('home', views.home, name="examiner_home"),
    path('questions/create', views.create_question, name="create_question"),
    path('questions/category/create', views.create_question_category, name="create_question_category"),
]