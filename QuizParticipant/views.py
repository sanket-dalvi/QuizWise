from django.shortcuts import render, get_object_or_404, redirect
from QuizWise.auth_decorator import examinee_required
from QuizCreator.models import Quiz, QuizQuestion, QuestionOption, Question, CategoryQuestionMap
from .models import Submission, UserQuizStatus, UserQuizScore
from django.db.models import Prefetch, Sum, Max
import random
from QuizWise.models import User
from django.contrib import messages
from difflib import SequenceMatcher



@examinee_required
def home(request):
    context = {}
    # Fetch the most recent quiz created by the logged-in user
    context['first_name'] = request.user.first_name
    context['last_name'] = request.user.last_name
    context['email'] = request.user.email
    context['contact'] = request.user.contact

    current_user = request.user
    recent_quizzes = (
    UserQuizScore.objects.filter(user=current_user)
            .values('quiz')
            .annotate(latest_timestamp=Max('timestamp'))
            .order_by('-latest_timestamp')
        )
    quiz_score_data = []

    for quiz in recent_quizzes:
        quiz_id = quiz['quiz']
        quiz_info = Quiz.objects.get(id=quiz_id)

        total_questions = quiz_info.total_questions
        user_quiz_scores = UserQuizScore.objects.filter(user=current_user, quiz=quiz_id)
        total_score = sum(score.score for score in user_quiz_scores)
        percentage = (total_score / (total_questions * 1.0)) * 100 if total_questions != 0 else 0
        
        quiz_data = {
            'quiz_name': quiz_info.name,
            'quiz_total_questions': total_questions,
            'total_score': total_score,
            'percentage': round(percentage, 2)  
        }
        quiz_score_data.append(quiz_data)

    context['quiz_scores'] = quiz_score_data

    available_quizzes = UserQuizStatus.objects.filter(user=current_user, status='Active').values('quiz').annotate(latest_timestamp=Max('timestamp')).order_by('-latest_timestamp')
    
    context['quizzes'] = available_quizzes

    return render(request, "QuizParticipant/home.html", context)


@examinee_required
def view_quizzes(request):
    user = request.user
    quiz_list = Quiz.objects.filter(visible = True)
    quizzes = []
    for quiz in quiz_list:
        user_quiz_status, created = UserQuizStatus.objects.get_or_create(
            user = user,
            quiz = quiz
        )
        if user_quiz_status.status == "Active":
            quizzes.append(quiz) 
    return render(request, "QuizParticipant/view_quizzes.html", { 'quizzes' : quizzes })


@examinee_required
def take_quiz(request, quiz_id):
    try:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        user_quiz_status = UserQuizStatus.objects.filter(user=request.user, quiz=quiz).first()
        if user_quiz_status.status == "Active":
            user_quiz_status.status = "Started"
            user_quiz_status.save()
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
                
            shuffled_questions = shuffled_questions[:quiz.total_questions]

            return render(request, "QuizParticipant/take_quiz.html", {'quiz': quiz, 'quiz_questions': shuffled_questions})
        elif user_quiz_status.status == "Started":
            messages.error(request, "You Have Already Attempted this Quiz")
            return redirect("view_quizzes")
            
    except Quiz.DoesNotExist:
        pass

    return render(request, "QuizParticipant/take_quiz.html")

@examinee_required
def profile(request):
    
    if request.method == "POST":
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            contact = request.POST.get('contact')

            user = get_object_or_404(User, pk=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.contact = contact
            user.save()
            messages.success(request, "User Details Updated Successfully")
        except Exception as e:
            messages.error(request, f"ERROR : {str(e)}")

    user = get_object_or_404(User, pk=request.user.id)

    context = {
        "first_name" : user.first_name,
        "last_name" : user.last_name,
        "email" : user.email,
        "contact" : user.contact
    }
    
    return render(request, "QuizParticipant/profile.html", context)


@examinee_required
def scores(request):
    user = request.user
    
    # Retrieve quizzes attempted by the user
    attempted_quizzes = UserQuizScore.objects.filter(user=user).values_list('quiz', flat=True).distinct()
    
    # Fetch quiz objects for the attempted quizzes
    quizzes = Quiz.objects.filter(id__in=attempted_quizzes)
    
    # Calculate total score for each quiz by the user and its percentage
    quiz_score_dict = {}
    for quiz in quizzes:
        total_score = UserQuizScore.objects.filter(user=user, quiz=quiz).aggregate(total_score=Sum('score'))
        quiz_score = total_score['total_score'] if total_score['total_score'] else 0
        
        # Calculate percentage
        total_questions = quiz.total_questions
        percentage = (quiz_score / (total_questions * 1.0)) * 100 if total_questions != 0 else 0
        
        quiz_score_dict[quiz.id] = {
            'score': quiz_score,
            'percentage': round(percentage, 2) 
        }

    # Prepare a list of dictionaries to include the quiz, its respective score, and percentage
    quiz_data = []
    for quiz in quizzes:
        score_data = quiz_score_dict.get(quiz.id, {'score': 0, 'percentage': 0})
        quiz_data.append({
            'quiz': quiz,
            'score': score_data['score'],
            'percentage': score_data['percentage']
        })

    context = {
        'quiz_data': quiz_data,
    }

    return render(request, "QuizParticipant/scores.html", context)


@examinee_required
def quiz_history(request):
    return render(request, "QuizParticipant/quiz_history.html")

@examinee_required
def submit_quiz(request, quiz_id):
    if request.method == 'POST':

        quiz = get_object_or_404(Quiz, pk=quiz_id)
        quiz_questions = QuizQuestion.objects.filter(quiz=quiz)

        total_questions = 0
        user_score = 0

        for quiz_question in quiz_questions:
            question = quiz_question.question
            question_id = str(question.id)
            user_answer = None
            is_correct = False
            question_score = 0

            if question_id in request.POST:
                if question.type.type_code == 'RB':
                    user_answer = request.POST.get(question_id)
                    is_correct = user_answer == question.answer
                    question_score = 1 if is_correct else 0
                elif question.type.type_code == 'CB':
                    user_answer = request.POST.getlist(question_id)
                    correct_answers = question.answer.replace("'","").replace("[","").replace("]","").split(', ')
                    is_correct = set(user_answer) == set(correct_answers)
                    if is_correct:
                        question_score = 1 
                    else:
                        total_correct_answers = len(correct_answers)
                        user_correct_answers = 0
                        for answer in correct_answers:
                            if answer in user_answer:
                                user_correct_answers += 1
                        if user_correct_answers == 0:
                            question_score = 0
                        elif total_correct_answers/user_correct_answers >= 0.5:
                            question_score = 0.5
                        else:
                            question_score = 0
                elif question.type.type_code == 'FT':
                    user_answer = request.POST.get(question_id)
                    
                    similarity_ratio = SequenceMatcher(None, str(user_answer).lower(), question.answer.lower()).ratio()
                    is_correct = similarity_ratio >= 0.8
                    question_score = 1 if is_correct else 0

                # Calculate scores
                user_score += question_score
                total_questions += 1

                # Save user score
                UserQuizScore.objects.create(
                    user=request.user,
                    quiz=quiz,
                    question=question,
                    score=question_score
                )

                # Save user submission
                Submission.objects.create(
                    user=request.user,
                    quiz=quiz,
                    question=question,
                    answer=user_answer
                )

        # Save or update user's quiz status
        user_quiz_status, created = UserQuizStatus.objects.get_or_create(
            user=request.user,
            quiz=quiz
        )
        if user_quiz_status.status == "Active":
            user_quiz_status.status = "Submitted"
            user_quiz_status.save()

        messages.success(request, f"Quiz Submitted Successfully.")

    return redirect("view_quizzes")
