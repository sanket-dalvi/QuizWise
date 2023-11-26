from django.shortcuts import render
from QuizWise.auth_decorator import examinee_required

@examinee_required
def home(request):
    return render(request, "QuizParticipant/home.html")
