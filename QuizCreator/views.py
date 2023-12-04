from django.shortcuts import render, redirect, get_object_or_404
from QuizWise.auth_decorator import examiner_required
from django.contrib import messages
from .models import Category, QuestionType, QuestionOption, Question, CategoryQuestionMap, Quiz, QuizQuestion, Group, GroupExamineeMapping
from QuizParticipant.models import UserQuizScore, UserQuizStatus
from QuizWise.models import User
from django.db.models import Q
from django.core.exceptions import ValidationError
import json
from django.db.models import Prefetch, Sum, F, FloatField
from django.http import JsonResponse
import statistics
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import seaborn as sns
import pandas as pd
import random


@examiner_required
def home(request):

    context = get_quiz_metrics(request)
    context['first_name'] = request.user.first_name
    context['last_name'] = request.user.last_name
    context['email'] = request.user.email
    context['contact'] = request.user.contact

    return render(request, "QuizCreator/home.html", context)

def get_quiz_metrics(request, quiz=None):
    current_user = request.user
    
    recent_quiz_score = UserQuizScore.objects.filter(
        quiz__created_by=current_user
    ).order_by('-timestamp').first()

    # If there is a recent quiz score, fetch associated quiz details
    if recent_quiz_score:
        recent_quiz = quiz
        if not quiz:
            recent_quiz = recent_quiz_score.quiz

        # Grouping scores by user and calculating total scores for each user
        user_total_scores = UserQuizScore.objects.filter(quiz=recent_quiz).values('user').annotate(
            total_score=Sum('score')
        )

        # Extracting total scores for mean, median, and mode calculations
        total_scores = [user['total_score'] for user in user_total_scores]

        # Calculating mean, median, and mode
        mean_score = statistics.mean(total_scores)
        median_score = statistics.median(total_scores)
        mode_score = statistics.mode(total_scores)

        # Calculating minimum and maximum total scores
        min_score = min(user_total_scores, key=lambda x: x['total_score'])['total_score']
        max_score = max(user_total_scores, key=lambda x: x['total_score'])['total_score']

        recent_quiz_metrics = {
            'quiz_name': recent_quiz.name,
            'duration': recent_quiz.duration,
            'total_questions': recent_quiz.total_questions,
            'min': min_score,
            'max': max_score,
            'mean': mean_score,
            'median': median_score,
            'mode': mode_score
        }
        # Creating a pandas DataFrame for visualization
        data = {
            'Metrics': ['Min', 'Max', 'Mode', 'Median', 'Mean'],
            'Scores': [min_score, max_score, mode_score, median_score, mean_score]
        }
        df = pd.DataFrame(data)

        # Generating bar plot
        plt.figure(figsize=(4, 2))
        sns.barplot(x='Metrics', y='Scores', data=df, palette='viridis')
        plt.title('Quiz Metrics')
        plt.xlabel('Metrics')
        plt.ylabel('Scores')
        plt.tight_layout()

        # Saving plot to BytesIO object
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        image_base64 = base64.b64encode(image_png).decode('utf-8')
        img_tag = f'<img src="data:image/png;base64,{image_base64} alt="Quiz Metrics" style="width: 70%; display: block; margin: 0 auto;"">'
    else:
        recent_quiz_metrics = None
        img_tag = None

    context = {
        'recent_quiz_metrics': recent_quiz_metrics,
        'img_tag': img_tag  
    }
    return context

@examiner_required
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
    

    return render(request, "QuizCreator/profile.html", context)


@examiner_required
def scores(request):

    quizzes = Quiz.objects.all()

    if request.method == 'POST':
        selected_quiz_id = request.POST.get('select-quiz')
        selected_quiz = Quiz.objects.filter(id=selected_quiz_id).first()
        
        # Fetch the user's score details for the selected quiz
        user_quiz_scores = UserQuizScore.objects.filter(quiz=selected_quiz)
        
        # Fetch distinct users who attempted the quiz
        distinct_users = user_quiz_scores.values_list('user', flat=True).distinct()

        quiz_data = []
        for user_id in distinct_users:
            user_scores = user_quiz_scores.filter(user_id=user_id)
            user_total_score = user_scores.aggregate(total_score=Sum('score'))['total_score'] or 0

            total_questions = QuizQuestion.objects.filter(quiz=selected_quiz).count()

            percentage = (
                user_total_score * 100.0 / (total_questions * 1.0)
            ) if total_questions > 0 else 0

            user_data = {
                'username': user_scores.first().user.username,
                'email': user_scores.first().user.email,
                'total_questions': total_questions,
                'score': user_total_score,
                'percentage': percentage
            }
            quiz_data.append(user_data)

        quiz_data.sort(key=lambda data: data['score'], reverse=True)
        context = {
            'total_submissions' : len(quiz_data),
            'quiz_data': quiz_data,
            'selected_quiz': selected_quiz,
            'quizzes' : quizzes,
        }
        if len(quiz_data) > 0:
            metric_context = get_quiz_metrics(request, selected_quiz)
            context.update(metric_context)

        return render(request, "QuizCreator/scores.html", context)


    context = {
        'quiz_data': [],
        'selected_quiz': None,
        'quizzes' : quizzes,
    }

    return render(request, "QuizCreator/scores.html", context)


@examiner_required
def quiz_history(request):
    return render(request, "QuizCreator/quiz_history.html")

@examiner_required
def create_question(request):
    if request.method == "POST":
        question_text = request.POST.get('question')
        question_type_code = request.POST.get('type')
        
        # Retrieve added options based on the naming convention
        radio_options = request.POST.getlist('radio-group')
        checkbox_options = request.POST.getlist('checkbox-group')

        # Retrieve selected answer values in radio group and checkbox group
        selected_radio = request.POST.get('radio-group')
        selected_checkbox = request.POST.getlist('checkbox-group')

        answer = request.POST.get("free-text-answer")

        options_json = request.POST.get('options')
        options = json.loads(options_json) if options_json else []

        # Check for empty fields
        if not question_text or not question_type_code:
            messages.error(request, "Please fill in all fields.")
            return redirect('create_question')

        # Check if options are added for radio or checkbox
        if question_type_code in ['RB', 'CB']:
            if not radio_options and question_type_code == 'RB':
                messages.error(request, "Please select correct answer option for the radio button.")
                return redirect('create_question')
            
            if not checkbox_options and question_type_code == 'CB':
                messages.error(request, "Please select correct answer options for the checkboxes.")
                return redirect('create_question')

        # Check if a correct answer is selected for radio or checkbox
        if question_type_code in ['RB', 'CB']:
            if not selected_radio and question_type_code == 'RB':
                messages.error(request, "Please select a correct answer for the radio button.")
                return redirect('create_question')
            
            if not options:
                messages.error(request, "Please add options.")
                return redirect('create_question')
            
            # If the question is a Free Text question, options list should be empty
            if question_type_code == 'FT':
                options = []
            elif question_type_code == 'RB':
                answer = selected_radio if selected_radio else ''
            elif question_type_code == 'CB':
                answer = selected_checkbox if selected_checkbox else []

        current_user = request.user

        try:
            # Creating the question object
            question = Question.objects.create(
                question=question_text,
                type=QuestionType.objects.get(type_code=question_type_code),
                answer=answer,  
                created_by=current_user,
            )
            
            # Creating QuestionOption objects for the options
            for option in options:
                QuestionOption.objects.create(question=question, option=option)
            
            messages.success(request, "Question created successfully.")
            return redirect('create_question')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('create_question')

    current_user = request.user
    question_types = QuestionType.objects.all()
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )
    return render(request, "QuizCreator/create_question.html", {'question_types': question_types})


@examiner_required
def create_question_category(request):
    if request.method == "POST":
        name = request.POST.get("category_name")
        description = request.POST.get("category_description")
        visible_to_others = request.POST.get("visible_to_others") == "on"

        
        if not name or not description:
            messages.error(request, "Please provide both name and description.")
            return render(request, "QuizCreator/create_question_category.html")

        try:
            existing_category = Category.objects.filter(name=name, created_by=request.user).exists()
            if existing_category:
                messages.error(request, "Category with the same name already exists for this user.")
                return render(request, "QuizCreator/create_question_category.html")

            category = Category.objects.create(
                name=name,
                description=description,
                visible_to_others=visible_to_others,
                created_by=request.user
            )
            messages.success(request, "Category created successfully.")
            
        except Exception as e:
            messages.error(request, f"Failed to create category: {e}")
            return render(request, "QuizCreator/create_question_category.html")

    return render(request, "QuizCreator/create_question_category.html")



@examiner_required
def view_questions(request):

    current_user = request.user
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )
    if request.method == "POST":
        selected_categories = request.POST.getlist('category-select')  
        selected_categories = [int(cat_id) for cat_id in selected_categories]
        if selected_categories :
            filtered_questions = Question.objects.filter(categoryquestionmap__category_id__in=selected_categories).select_related('type').prefetch_related(
                Prefetch('options', queryset=QuestionOption.objects.all()),
                Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
            ).distinct()
        else:
            filtered_questions = Question.objects.select_related('type').prefetch_related(
                Prefetch('options', queryset=QuestionOption.objects.all()),
                Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
            ).all()

        return render(request, 'QuizCreator/questions.html', {'questions': filtered_questions,  'categories': categories, 'selected_categories': selected_categories})
    
    questions = Question.objects.select_related('type').prefetch_related(
        Prefetch('options', queryset=QuestionOption.objects.all()),
        Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
    ).all()
    

    return render(request, 'QuizCreator/questions.html', {'questions': questions, 'categories': categories})

 
@examiner_required
def edit_questions(request):

    questions = Question.objects.all()
    current_user = request.user
    question_types = QuestionType.objects.all()
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )   


@examiner_required
def edit_questions(request):

    current_user = request.user
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )
    if request.method == "POST":
        selected_categories = request.POST.getlist('category-select') 
        selected_categories = [int(cat_id) for cat_id in selected_categories]
        if selected_categories :
            filtered_questions = Question.objects.filter(categoryquestionmap__category_id__in=selected_categories).select_related('type').prefetch_related(
                Prefetch('options', queryset=QuestionOption.objects.all()),
                Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
            ).distinct()
        else:
            filtered_questions = Question.objects.select_related('type').prefetch_related(
                Prefetch('options', queryset=QuestionOption.objects.all()),
                Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
            ).all()

        return render(request, 'QuizCreator/edit_questions.html', {'questions': filtered_questions,  'categories': categories, 'selected_categories': selected_categories})
    
    questions = Question.objects.select_related('type').prefetch_related(
        Prefetch('options', queryset=QuestionOption.objects.all()),
        Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
    ).all()
    

    return render(request, 'QuizCreator/edit_questions.html', {'questions': questions, 'categories': categories})

@examiner_required
def delete_question(request, question_id):
    try:
        question = get_object_or_404(Question, pk=question_id)
        question.delete()
    except Question.DoesNotExist as e:
        messages.error(f"ERROR :  Could Not Delete Question {str(e)}")
    messages.success(request, "Question Has Been Deleted Successfully")
    return redirect("edit_questions")

@examiner_required
def map_question_category(request):

    if request.method == 'POST':
        checkbox_values = request.POST.getlist('checkbox-group')  

        selected_categories = request.POST.getlist('category-select')  
        for checkbox_value in checkbox_values:
            question_id = int(checkbox_value)
            # For each selected question, create or update CategoryQuestionMap records
            for category_id in selected_categories:
                category = Category.objects.filter(id=category_id).first()
                question = Question.objects.filter(id=question_id).first()
                CategoryQuestionMap.objects.update_or_create(
                    question=question,
                    category=category
                )
        messages.success(request, "Mapping Added Succesfully")

    questions = Question.objects.select_related('type').prefetch_related(
        Prefetch('options', queryset=QuestionOption.objects.all()),
        Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
    ).all()
    
    current_user = request.user
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )

    return render(request, "QuizCreator/question_category_map.html", {'questions': questions, 'categories': categories})


@examiner_required
def create_quiz(request):
    if request.method == 'POST':
        quiz_name = request.POST.get('quiz-name')
        quiz_description = request.POST.get('quiz-description')
        quiz_duration = request.POST.get('quiz-duration')
        quiz_total_questions = request.POST.get('quiz-total-questions')
        quiz_passcode = request.POST.get('passcode')

        # Creating a new Quiz instance and saving it to the database
        new_quiz = Quiz(
            name=quiz_name,
            description=quiz_description,
            duration=quiz_duration,
            total_questions=quiz_total_questions,
            passcode=quiz_passcode,
            created_by = request.user,
            modified_by = request.user
        )
        new_quiz.save()
        messages.success(request, 'Quiz created successfully!')

    return render(request, "QuizCreator/create_quiz.html")


@examiner_required
def edit_quiz(request):

    quizzes = Quiz.objects.all()
    selected_quiz = None

    if request.method == 'POST':
        selected_quiz_id = request.POST.get('select-quiz')
        selected_quiz_id = int(selected_quiz_id)

        # Retrieve selected quiz details
        selected_quiz = Quiz.objects.get(id=selected_quiz_id)

    return render(request, 'QuizCreator/edit_quiz.html', {'quizzes': quizzes, 'selected_quiz': selected_quiz})


@examiner_required
def update_quiz(request):
    if request.method == 'POST':
        quiz_id = request.POST.get('quiz-id')
        selected_quiz = Quiz.objects.get(pk=quiz_id)

        selected_quiz.name = request.POST.get('quiz-name')
        selected_quiz.description = request.POST.get('quiz-description')
        selected_quiz.duration = request.POST.get('quiz-duration')
        selected_quiz.total_questions = request.POST.get('quiz-total-questions')
        selected_quiz.visible = request.POST.get('quiz-visible') == 'on'
        selected_quiz.passcode = request.POST.get('quiz-passcode')
        selected_quiz.modified_by = request.user
        selected_quiz.save()

        messages.success(request, 'Quiz details updated successfully.')
        return redirect('edit_quiz')  

    quizzes = Quiz.objects.all()
    return render(request, 'QuizCreator/edit_quiz.html', {'quizzes': quizzes})

@examiner_required
def delete_quiz(request):
    return redirect("edit_quiz")

@examiner_required
def post_quiz(request):
    quizzes = Quiz.objects.filter(visible=False)
    groups = Group.objects.all()
    context = {
        'quizzes': quizzes, 
        'groups': groups
    }
    if request.method == "POST":
        form_type = request.POST.get('form-type')
        if form_type == 'select-group':
            group_id = request.POST.get('select-group')
            group = Group.objects.get(id=int(group_id))
            group_examinees = [mapping.user for mapping in GroupExamineeMapping.objects.filter(group=group)]
            context['group_examinees'] = group_examinees
            context['selected_group'] = group
        else:
            group_id = request.POST.get('group_id')
            group = Group.objects.get(id=int(group_id))
            quiz_id = request.POST.get('select-quiz')
            quiz = Quiz.objects.get(id=int(quiz_id))
            quiz_participants = request.POST.getlist('checkbox-group')
            for user_id in quiz_participants:
                user = User.objects.get(id=user_id)
                user_quiz_status = UserQuizStatus.objects.get(user=user, quiz=quiz)
                if not user_quiz_status:
                    UserQuizStatus.objects.create(user=user,quiz=quiz)

            context['selected_quiz'] = quiz
            context['selected_group'] = group
            messages.success(request, "Quiz Posted To Selected Participants")


    return render(request, 'QuizCreator/post_quiz.html', context)

@examiner_required
def add_quiz_questions(request):
    total_questions_added = 0
    quiz_questions = []
    quizzes = Quiz.objects.all()
    remaining_questions = None
    selected_quiz = None
    current_user = request.user
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )
    questions = Question.objects.select_related('type').prefetch_related(
        Prefetch('options', queryset=QuestionOption.objects.all()),
        Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
    ).all()


    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "add_quiz_questions":
            quiz_id = request.POST.get("selected_quiz_id")
            selected_questions = request.POST.getlist('checkbox-group')
            try:

                quiz = get_object_or_404(Quiz, pk=quiz_id)

                for question_id in selected_questions:
                    # Check if the mapping already exists
                    existing_mapping = QuizQuestion.objects.filter(quiz=quiz, question_id=question_id).exists()
                    if not existing_mapping:
                        # If the mapping doesn't exist, create it
                        question = get_object_or_404(Question, pk=question_id)
                        quiz_question = QuizQuestion.objects.create(quiz=quiz, question=question)
                      
                        
                        # Save the quiz-question mapping
                        quiz_question.save()
                messages.success(request, "Questions Added Successfully")
                quiz_question_objects = QuizQuestion.objects.filter(quiz = quiz)
                total_questions_added = quiz_question_objects.count()
                remaining_questions = quiz.total_questions - total_questions_added
                quiz_questions = Question.objects.select_related('type').prefetch_related(
                    Prefetch('options', queryset=QuestionOption.objects.all()),
                    Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
                ).filter(quizquestion__in=quiz_question_objects).all()
                
            except Quiz.DoesNotExist:
                messages.error(request, "ERROR : Invalid Quiz Id")
            selected_quiz = get_object_or_404(Quiz, pk=quiz_id)
        elif form_type == "select_quiz":
            quiz_id = request.POST.get("select-quiz")
            selected_quiz_id = quiz_id
            try:

                quiz = get_object_or_404(Quiz, pk=quiz_id)
                quiz_question_objects = QuizQuestion.objects.filter(quiz = quiz)
                total_questions_added = quiz_question_objects.count()
                remaining_questions = quiz.total_questions - total_questions_added
                quiz_questions = Question.objects.select_related('type').prefetch_related(
                    Prefetch('options', queryset=QuestionOption.objects.all()),
                    Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
                ).filter(quizquestion__in=quiz_question_objects).all()
                
            except Quiz.DoesNotExist:
                messages.error(request, "ERROR : Invalid Quiz Id")
            selected_quiz = get_object_or_404(Quiz, pk=selected_quiz_id)
        elif form_type == "question_search_by_category":
            quiz_id = request.POST.get("selected_quiz_id")
            selected_quiz_id = quiz_id
            selected_categories = request.POST.getlist('category-select')  # Retrieve selected categories
            selected_categories = [int(cat_id) for cat_id in selected_categories]
            if selected_categories :
                questions = Question.objects.filter(categoryquestionmap__category_id__in=selected_categories).select_related('type').prefetch_related(
                    Prefetch('options', queryset=QuestionOption.objects.all()),
                    Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
                ).distinct()
            else:
                questions = Question.objects.select_related('type').prefetch_related(
                    Prefetch('options', queryset=QuestionOption.objects.all()),
                    Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
                ).all()
            try:

                quiz = get_object_or_404(Quiz, pk=quiz_id)
                quiz_question_objects = QuizQuestion.objects.filter(quiz = quiz)
                total_questions_added = quiz_question_objects.count()
                remaining_questions = quiz.total_questions - total_questions_added
                quiz_questions = Question.objects.select_related('type').prefetch_related(
                    Prefetch('options', queryset=QuestionOption.objects.all()),
                    Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
                ).filter(quizquestion__in=quiz_question_objects).all()
                
            except Quiz.DoesNotExist:
                messages.error(request, "ERROR : Invalid Quiz Id")
            selected_quiz = get_object_or_404(Quiz, pk=selected_quiz_id)
    question_id_list = []
    for question in quiz_questions:
        question_id_list.append(question.id)
    if remaining_questions:
        if remaining_questions < 0:
            remaining_questions = 0
    return render(request, 'QuizCreator/modify_quiz_questions.html', {'quizzes': quizzes, 'categories' : categories, 'questions' : questions, 'quiz_questions': quiz_questions, 'total_questions_added' : total_questions_added, 'selected_quiz' : selected_quiz, 'question_id_list' : question_id_list, 'remaining_questions' : remaining_questions})

@examiner_required
def make_quiz_visible(request):
    if request.method == "POST":
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = get_object_or_404(Quiz, pk=quiz_id)
            quiz.visible = True
            quiz.save()
            messages.success(request, "Quiz Has Been Posted Successfully")
        except Quiz.DoesNotExist:
            messages.error(request, "Error: Could Not Made Quiz Available. Try Again")

    return redirect('add_quiz_questions')

@examiner_required
def delete_quiz_questions(request):

    if request.method == "POST":
        
        question_ids = request.POST.getlist("delete-checkbox-group")
        quiz_id = request.POST.get("selected_quiz_id")

        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            
            for question_id in question_ids:

                question = Question.objects.get(pk=question_id)

                # Delete the quiz-question mapping if it exists
                QuizQuestion.objects.filter(quiz=quiz, question=question).delete()
            messages.success(request, "Questions Deleted")
            
        except (Quiz.DoesNotExist, Question.DoesNotExist) as e:
            messages.error(request, "ERROR : Could Not Delete ")
            
        return redirect("add_quiz_questions")
    

@examiner_required
def preview_quiz(request):
    quizzes = Quiz.objects.all()

    if request.method == "POST":
        quiz_id = request.POST.get("select-quiz")
        try:
            quiz = get_object_or_404(Quiz, pk=quiz_id)
            quiz_question_objects = QuizQuestion.objects.filter(quiz = quiz)
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
            
        except Quiz.DoesNotExist:
            messages.error(request, "ERROR : Invalid Quiz Id")
        return render(request, "QuizCreator/show_preview.html", {'quiz' : quiz,'quiz_questions' : shuffled_questions})
        
    return render(request, "QuizCreator/preview_quiz.html", {'quizzes' : quizzes})



@examiner_required
def add_examinee_to_group(request):
    group_id = None
    # If the request method is not POST, render the form template
    groups = Group.objects.filter(created_by=request.user)
    examinees = User.objects.filter(is_examinee=True)

    if request.method == 'POST':
        form_type = request.POST.get('form-type')
        if form_type == 'select-group' :
            group_id = int(request.POST.get('select-group'))
            group = Group.objects.get(id=group_id)
            group_examinees = GroupExamineeMapping.objects.filter(group=group)
            examinee_ids = []

            for group_examinee in group_examinees:
                examinee_ids.append(group_examinee.user.id)

            
            return render(request, 'QuizCreator/add_examinee_to_group.html', {'group_id': group_id, 'examinees' : examinees, 'groups': groups, 'examinee_ids': examinee_ids})

        elif form_type == 'add-examinees':
            group_id = request.POST.get('selected-group')
            selected_examinees = request.POST.getlist('checkbox-group')
            group = Group.objects.get(id=group_id)
            existing_mapping = GroupExamineeMapping.objects.filter(group=group)
            for existing in existing_mapping:
                id =  str(existing.user.id)
                if id not in selected_examinees:
                    existing.delete()
            # Create GroupExamineeMapping instances for each selected examinee
            for examinee_id in selected_examinees:
                examinee = User.objects.get(id=examinee_id)
                GroupExamineeMapping.objects.get_or_create(group=group, user=examinee)
                
            # Add a success message
            messages.success(request, 'Examinees added to the group successfully!')
            return render(request, 'QuizCreator/add_examinee_to_group.html', {'examinees' : examinees, 'groups': groups})

    return render(request, 'QuizCreator/add_examinee_to_group.html', {'group_id': group_id, 'examinees': examinees, 'groups': groups})


@examiner_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group-name')
        group_description = request.POST.get('group-description')

        # Create a new group instance
        new_group = Group(
            name=group_name,
            description=group_description,
        )
        # Save the group to the database
        new_group.save()

        # Optionally, you can add a success message using Django's messages framework
        messages.success(request, 'Group created successfully!')

        # Redirect to a different page or template if needed
        return redirect('create_group')

    # If the request method is not POST, render the form template
    return render(request, 'QuizCreator/create_group.html')


"""
@examiner_required
def view_group(request):
    groups = Groups.objects.all()
    return render(request, 'QuizCreator/view_group.html',  {'groups': groups})"""


@examiner_required
def view_group(request):
    groups = Group.objects.filter(created_by=request.user)
    selected_group_id = None
    examinees = []

    if request.method == 'POST':
        selected_group_id = request.POST.get('select-group')
        selected_group = Group.objects.get(id=selected_group_id)
        # Assuming 'groups' is the ForeignKey field in the User model pointing to the Groups model
        mappings = GroupExamineeMapping.objects.filter(group=selected_group)
        examinees = []
        for mapping in mappings:
            examinees.append(mapping.user)

        return render(request, "QuizCreator/view_group.html", {"examinees" : examinees, 'groups': groups, 'group_id': selected_group_id})

    return render(request, 'QuizCreator/view_group.html', {
        'groups': groups,
        'selected_group_id': selected_group_id,
        'examinees': examinees,
    })