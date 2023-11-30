from django.shortcuts import render
from QuizWise.auth_decorator import examinee_required

@examinee_required
def home(request):
    return render(request, "QuizParticipant/home.html")

@examinee_required
def profile(request):
    return render(request, "QuizParticipant/profile.html")


@examinee_required
def scores(request):
    return render(request, "QuizParticipant/scores.html")


@examinee_required
def quiz_history(request):
    return render(request, "QuizParticipant/quiz_history.html")
