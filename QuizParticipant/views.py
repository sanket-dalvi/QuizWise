from django.shortcuts import render, get_object_or_404
from QuizWise.auth_decorator import examinee_required
from QuizCreator.models import Quiz, QuizQuestion, QuestionOption, Question, CategoryQuestionMap
from django.db.models import Prefetch
import random



@examinee_required
def home(request):
    return render(request, "QuizParticipant/home.html")


@examinee_required
def view_quizzes(request):
    quizzes = Quiz.objects.filter(visible = True)
    return render(request, "QuizParticipant/view_quizzes.html", { 'quizzes' : quizzes })


@examinee_required
def take_quiz(request, quiz_id):
    try:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        quiz_question_objects = QuizQuestion.objects.filter(quiz=quiz)
        quiz_questions = Question.objects.select_related('type').prefetch_related(
            Prefetch('options', queryset=QuestionOption.objects.all()),
            Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
        ).filter(quizquestion__in=quiz_question_objects).all()

        # Shuffle questions
        shuffled_questions = list(quiz_questions)
        random.shuffle(shuffled_questions)

        # Shuffle options for each question
        for question in shuffled_questions:
            question_options = list(question.options.all())
            random.shuffle(question_options)
            question.options.set(question_options)

        return render(request, "QuizParticipant/take_quiz.html", {'quiz': quiz, 'quiz_questions': shuffled_questions})
        
    except Quiz.DoesNotExist:
        pass

    return render(request, "QuizParticipant/take_quiz.html")
