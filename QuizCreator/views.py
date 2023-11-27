from django.shortcuts import render, redirect
from QuizWise.auth_decorator import examiner_required
from django.contrib import messages
from .models import Category, QuestionType
from django.db.models import Q
from django.core.exceptions import ValidationError
import json




@examiner_required
def home(request):
    return render(request, "QuizCreator/home.html")


@examiner_required
def create_question(request):
    if request.method == "POST":
        category = request.POST.get('category')
        question = request.POST.get('question')
        question_type = request.POST.get('type')
        
        # Retrieve added options based on the naming convention
        radio_options = request.POST.getlist('radio-group')
        checkbox_options = request.POST.getlist('checkbox-group')

        # Retrieve selected answer value in radio group
        selected_radio = request.POST.get('radio-group')

        options_json = request.POST.get('options')
        options = json.loads(options_json) if options_json else []
        print(options)
        # Retrieve selected answer values in checkbox group
        selected_checkboxes = request.POST.getlist('checkbox-group')

        # Check for empty fields
        if not category or not question or not question_type:
            messages.error(request, "Please fill in all fields.")
            

        # Check if options are added for radio or checkbox
        if question_type in ['RB', 'CB']:
            if not radio_options and question_type == 'RB':
                messages.error(request, "Please add options for the radio button.")
            
            if not checkbox_options and question_type == 'CB':
                messages.error(request, "Please add options for the checkboxes.")

        # Check if a correct answer is selected for radio or checkbox
        if question_type in ['RB', 'CB']:
            if not selected_radio and question_type == 'RB':
                messages.error(request, "Please select a correct answer for the radio button.")
            
            if not selected_checkboxes and question_type == 'CB':
                messages.error(request, "Please select at least one correct answer for the checkboxes.")

        print(radio_options)
        print(selected_radio)

    current_user = request.user
    question_types = QuestionType.objects.all()
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )
    return render(request, "QuizCreator/create_question.html", {'categories': categories, 'question_types': question_types})

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
