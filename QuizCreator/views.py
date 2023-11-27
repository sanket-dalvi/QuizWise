from django.shortcuts import render, redirect
from QuizWise.auth_decorator import examiner_required
from django.contrib import messages
from .models import Category, QuestionType, QuestionOption, Question, CategoryQuestionMap
from django.db.models import Q
from django.core.exceptions import ValidationError
import json
from django.db.models import Prefetch


@examiner_required
def home(request):
    return render(request, "QuizCreator/home.html")


@examiner_required
def create_question(request):
    if request.method == "POST":
        question_text = request.POST.get('question')
        question_type_code = request.POST.get('type')
        
        # Retrieve added options based on the naming convention
        radio_options = request.POST.getlist('radio-group')
        checkbox_options = request.POST.getlist('checkbox-group')

        # Retrieve selected answer value in radio group
        selected_radio = request.POST.get('radio-group')
        selected_checkbox = request.POST.get('checkbox-group')

        options_json = request.POST.get('options')
        options = json.loads(options_json) if options_json else []

        # Check for empty fields
        if not question_text or not question_type_code:
            messages.error(request, "Please fill in all fields.")
            return redirect('create_question')

        # Check if options are added for radio or checkbox
        if question_type_code in ['RB', 'CB']:
            if not radio_options and question_type_code == 'RB':
                messages.error(request, "Please add options for the radio button.")
                return redirect('create_question')
            
            if not checkbox_options and question_type_code == 'CB':
                messages.error(request, "Please add options for the checkboxes.")
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
                answer = selected_checkbox if selected_checkbox else ''

        current_user = request.user

        try:
            # Creating the question object
            question = Question.objects.create(
                question=question_text,
                type=QuestionType.objects.get(type_code=question_type_code),
                answer=answer,  # Modify this based on your answer logic
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

        # Validation
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

    questions = Question.objects.all()
    current_user = request.user
    question_types = QuestionType.objects.all()
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )

@examiner_required
def view_questions(request):
    questions = Question.objects.select_related('type').prefetch_related(
        Prefetch('options', queryset=QuestionOption.objects.all()),
        Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
    ).all()
    
    current_user = request.user
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )

    return render(request, 'QuizCreator/questions.html', {'questions': questions, 'categories': categories})

@examiner_required
def map_question_category(request):
    questions = Question.objects.select_related('type').prefetch_related(
        Prefetch('options', queryset=QuestionOption.objects.all()),
        Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
    ).all()
    
    current_user = request.user
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )

    return render(request, "QuizCreator/question_category_map.html", {'questions': questions, 'categories': categories})
