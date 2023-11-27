from django.shortcuts import render
from QuizWise.auth_decorator import examiner_required

@examiner_required
def home(request):
    return render(request, "QuizCreator/home.html")

