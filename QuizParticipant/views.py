from django.shortcuts import render, get_object_or_404, redirect
from QuizWise.auth_decorator import examinee_required
from QuizCreator.models import Quiz, QuizQuestion, QuestionOption, Question, CategoryQuestionMap
from .models import Submission, UserQuizStatus, UserQuizScore
from django.db.models import Prefetch, Sum, Max
import random
from QuizWise.models import User
from django.contrib import messages
from difflib import SequenceMatcher
from QuizWise.decorators import log_view



@log_view
@examinee_required
def home(request):
    # View function for the home page of an examinee.
    context = {}
    # Add user information to the context
    context['first_name'] = request.user.first_name
    context['last_name'] = request.user.last_name
    context['email'] = request.user.email
    context['contact'] = request.user.contact
    current_user = request.user

    # Retrieve recent quizzes and their scores for the user
    recent_quizzes = (
    UserQuizScore.objects.filter(user=current_user)
            .values('quiz')
            .annotate(latest_timestamp=Max('timestamp'))
            .order_by('-latest_timestamp')
        )
    quiz_score_data = []

    # Process recent quizzes and calculate scores
    for quiz in recent_quizzes:
        quiz_id = quiz['quiz']
        quiz_info = Quiz.objects.get(id=quiz_id)
        total_questions = quiz_info.total_questions
        user_quiz_scores = UserQuizScore.objects.filter(user=current_user, quiz=quiz_id)
        total_score = sum(score.score for score in user_quiz_scores)
        percentage = (total_score / (total_questions * 1.0)) * 100 if total_questions != 0 else 0

        # Add quiz score data to the list
        quiz_data = {
            'quiz_name': quiz_info.name,
            'quiz_total_questions': total_questions,
            'total_score': total_score,
            'percentage': round(percentage, 2)  
        }
        quiz_score_data.append(quiz_data)

    context['quiz_scores'] = quiz_score_data
    
    # Retrieve available quizzes for the user
    available_quizzes = []
    quiz_list = Quiz.objects.filter(visible = True)
    for quiz in quiz_list:
        user_quiz_status = UserQuizStatus.objects.filter(
            user = request.user,
            quiz = quiz
        ).first()
        if user_quiz_status and user_quiz_status.status == "Active":
            available_quizzes.append(quiz) 
    context['quizzes'] = available_quizzes

    return render(request, "QuizParticipant/home.html", context)


@log_view
@examinee_required
def view_quizzes(request):
    # Retrieve the current user
    user = request.user
    # Filter quizzes based on visibility
    quiz_list = Quiz.objects.filter(visible = True)
    quizzes = []

    # Check the status of each quiz for the current user
    for quiz in quiz_list:
        user_quiz_status = UserQuizStatus.objects.filter(
            user = user,
            quiz = quiz
        ).first()
        if user_quiz_status and user_quiz_status.status == "Active":
            quizzes.append(quiz) 
    return render(request, "QuizParticipant/view_quizzes.html", { 'quizzes' : quizzes })


@log_view
@examinee_required
def take_quiz(request, quiz_id):
    # View function to initiate and handle the process of an examinee taking a quiz.
    try:
        # Retrieve the quiz object or raise a 404 error if not found
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        user_quiz_status = UserQuizStatus.objects.filter(user=request.user, quiz=quiz).first()

        if user_quiz_status.status == "Active":
            # Update user's quiz status to "Started" once the quiz is initiated
            user_quiz_status.status = "Started"
            user_quiz_status.save()

            # Retrieve the quiz questions for the specified quiz
            quiz_question_objects = QuizQuestion.objects.filter(quiz=quiz)
            quiz_questions = Question.objects.select_related('type').prefetch_related(
                Prefetch('options', queryset=QuestionOption.objects.all()),
                Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
            ).filter(quizquestion__in=quiz_question_objects).all()

            # Shuffle the order of questions and their options
            shuffled_questions = list(quiz_questions)
            random.shuffle(shuffled_questions)
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

@log_view
@examinee_required
def profile(request):
    # View function to display and update the profile details of the logged-in examinee.
    if request.method == "POST":
        try:
            # Retrieve updated user profile details from the POST request
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            contact = request.POST.get('contact')
            email_notification = request.POST.get('email_notification')
            mobile_notification = request.POST.get('mobile_notification')
            email_notification = email_notification == 'on'  
            mobile_notification = mobile_notification == 'on'

            # Retrieve the user object and update its details
            user = get_object_or_404(User, pk=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.contact = contact
            user.email_notification = email_notification
            user.mobile_notification = mobile_notification
            user.save()
            messages.success(request, "User Details Updated Successfully")
        except Exception as e:
            messages.error(request, f"ERROR : {str(e)}")

    # Retrieve the user object for rendering the profile page
    user = get_object_or_404(User, pk=request.user.id)
    
    # Prepare context with user's profile data for rendering
    context = {
        "first_name" : user.first_name,
        "last_name" : user.last_name,
        "email" : user.email,
        "contact" : user.contact,
        "email_notification" : user.email_notification,
        "mobile_notification" : user.mobile_notification
    }
    # Render the 'profile.html' template with user's profile data
    return render(request, "QuizParticipant/profile.html", context)


@log_view
@examinee_required
def scores(request):
    # View function to display the scores of quizzes attempted by the logged-in examinee.
    user = request.user
    # Get the list of quizzes attempted by the user
    attempted_quizzes = UserQuizScore.objects.filter(user=user).values_list('quiz', flat=True).distinct()
    quizzes = Quiz.objects.filter(id__in=attempted_quizzes)
    quiz_score_dict = {}

    # Calculate scores and percentages for each quiz
    for quiz in quizzes:
        total_score = UserQuizScore.objects.filter(user=user, quiz=quiz).aggregate(total_score=Sum('score'))
        quiz_score = total_score['total_score'] if total_score['total_score'] else 0
        total_questions = quiz.total_questions
        percentage = (quiz_score / (total_questions * 1.0)) * 100 if total_questions != 0 else 0
        
        quiz_score_dict[quiz.id] = {
            'score': quiz_score,
            'percentage': round(percentage, 2) 
        }

    # Prepare quiz data for rendering
    quiz_data = []
    for quiz in quizzes:
        score_data = quiz_score_dict.get(quiz.id, {'score': 0, 'percentage': 0})
        quiz_data.append({
            'quiz': quiz,
            'score': score_data['score'],
            'percentage': score_data['percentage']
        })

    # Render the 'scores.html' template with quiz data
    context = {
        'quiz_data': quiz_data,
    }
    return render(request, "QuizParticipant/scores.html", context)


@log_view
@examinee_required
def quiz_history(request):
    return render(request, "QuizParticipant/quiz_history.html")

@log_view
@examinee_required
def submit_quiz(request, quiz_id):

    #Handle the submission of a quiz by an examinee.
    if request.method == 'POST':
        # Retrieve the quiz and its questions
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        quiz_questions = QuizQuestion.objects.filter(quiz=quiz)
        total_questions = 0
        user_score = 0
        # Process each question in the quiz
        for quiz_question in quiz_questions:
            question = quiz_question.question
            question_id = str(question.id)
            user_answer = None
            is_correct = False
            question_score = 0

            # Check if the question ID is present in the submitted POST data
            if question_id in request.POST:
                # Process different question types: Radio Button (RB), Checkbox (CB), and Free Text (FT)
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
                    # Check similarity ratio for free-text questions
                    similarity_ratio = SequenceMatcher(None, str(user_answer).lower(), question.answer.lower()).ratio()
                    is_correct = similarity_ratio >= 0.8
                    question_score = 1 if is_correct else 0
                
                # Update user's total score and record the submission
                user_score += question_score
                total_questions += 1
                UserQuizScore.objects.create(
                    user=request.user,
                    quiz=quiz,
                    question=question,
                    score=question_score
                )

                Submission.objects.create(
                    user=request.user,
                    quiz=quiz,
                    question=question,
                    answer=user_answer
                )

        # Update user's quiz status to "Submitted" if the status is "Active"
        user_quiz_status, created = UserQuizStatus.objects.get_or_create(
            user=request.user,
            quiz=quiz
        )
        if user_quiz_status.status == "Active":
            user_quiz_status.status = "Submitted"
            user_quiz_status.save()
        messages.success(request, f"Quiz Submitted Successfully.")
    return redirect("view_quizzes")
