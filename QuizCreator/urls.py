from django.urls import path, include
from . import views

urlpatterns = [
    path('home', views.home, name="examiner_home"),
    path('home/profile', views.profile, name="examiner_profile"),
    path('home/scores', views.scores, name="examiner_scores"),
    path('home/quiz_history', views.quiz_history, name="examiner_quiz_history"),
    path('questions/create', views.create_question, name="create_question"),
    path('questions', views.view_questions, name="view_questions"),
    path('questions/category/create', views.create_question_category, name="create_question_category"),
    path('questions/category/map', views.map_question_category, name="map_question_category"),
    path('quiz/create', views.create_quiz, name="create_quiz"),
    path('quiz/edit', views.edit_quiz, name="edit_quiz"),
    path('quiz/update', views.update_quiz, name="update_quiz"),
    path('quiz/delete', views.delete_quiz, name="delete_quiz"),
    path('quiz/preview', views.preview_quiz, name="preview_quiz"),
    path('quiz/modify_questions', views.add_quiz_questions, name="add_quiz_questions"),
    path('quiz/delete_questions', views.delete_quiz_questions, name="delete_quiz_questions"),
    path('questions/category/edit', views.edit_questions, name="edit_questions"),
    path('quiz/make_quiz_visible', views.make_quiz_visible, name="make_quiz_visible"),
    
]