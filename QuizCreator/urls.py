from django.urls import path, include
from . import views

urlpatterns = [
    path('home', views.home, name="examiner_home"),
    path('questions/create', views.create_question, name="create_question"),
    path('questions', views.view_questions, name="view_questions"),
    path('questions/category/create', views.create_question_category, name="create_question_category"),
    path('questions/category/map', views.map_question_category, name="map_question_category"),
    path('quiz/create', views.create_quiz, name="create_quiz"),
    path('quiz/edit', views.edit_quiz, name="edit_quiz"),
    path('quiz/update', views.update_quiz, name="update_quiz"),
    path('quiz/delete', views.delete_quiz, name="delete_quiz"),
    path('questions/category/edit', views.edit_questions, name="edit_questions"),
    
]