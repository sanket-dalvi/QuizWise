from django.shortcuts import render, redirect, get_object_or_404
from QuizWise.auth_decorator import examiner_required
from django.contrib import messages
from .models import Category, QuestionType, QuestionOption, Question, CategoryQuestionMap, Quiz, QuizQuestion
from django.db.models import Q
from django.core.exceptions import ValidationError
import json
from django.db.models import Prefetch
from django.http import JsonResponse



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

        # Retrieve selected answer values in radio group and checkbox group
        selected_radio = request.POST.get('radio-group')
        selected_checkbox = request.POST.getlist('checkbox-group')

        answer = request.POST.get("free-text-answer").strip()

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
                answer = selected_checkbox if selected_checkbox else []

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

    current_user = request.user
    categories = Category.objects.filter(
        Q(created_by=current_user) | Q(visible_to_others=True)
    )
    if request.method == "POST":
        selected_categories = request.POST.getlist('category-select')  # Retrieve selected categories
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
        selected_categories = request.POST.getlist('category-select')  # Retrieve selected categories
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
    

    return render(request, 'QuizCreator/edit_questions.html', {'questions': questions, 'categories': categories})


@examiner_required
def map_question_category(request):

    if request.method == 'POST':
        checkbox_values = request.POST.getlist('checkbox-group')  # Retrieve selected checkbox values

        selected_categories = request.POST.getlist('category-select')  # Retrieve selected categories
        # 'category-select' corresponds to the name attribute of your category <select> element

        # Process the checkbox values and selected categories
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
        quiz_visible = request.POST.get('quiz-visible') == 'on'

        # Creating a new Quiz instance and saving it to the database
        new_quiz = Quiz(
            name=quiz_name,
            description=quiz_description,
            duration=quiz_duration,
            total_questions=quiz_total_questions,
            visible=quiz_visible
        )
        new_quiz.save()
        messages.success(request, 'Quiz created successfully!')

    return render(request, "QuizCreator/create_quiz.html")


@examiner_required
def edit_quiz(request):
    if request.method == 'POST':
        selected_quiz_id = request.POST.get('select-quiz')

        # Retrieve selected quiz details
        selected_quiz = Quiz.objects.get(id=selected_quiz_id)

        return render(request, 'QuizCreator/edit_quiz.html', {'selected_quiz': selected_quiz})

    quizzes = Quiz.objects.all()
    return render(request, 'QuizCreator/edit_quiz.html', {'quizzes': quizzes})


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
        selected_quiz.save()

        messages.success(request, 'Quiz details updated successfully.')
        return redirect('your_redirect_url')  # Redirect to the desired URL after updating

    quizzes = Quiz.objects.all()
    return render(request, 'QuizCreator/edit_quiz.html', {'quizzes': quizzes})

@examiner_required
def delete_quiz(request):
    return redirect("edit_quiz")


@examiner_required
def add_quiz_questions(request):
    total_questions_added = 0
    quiz_questions = []
    quizzes = Quiz.objects.all()
    selected_quiz_id = None
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
                        # Perform any additional operations if required
                        
                        # Save the quiz-question mapping
                        quiz_question.save()
                messages.success(request, "Questions Added Successfully")
                quiz_question_objects = QuizQuestion.objects.filter(quiz = quiz)
                total_questions_added = quiz_question_objects.count()
                quiz_questions = Question.objects.select_related('type').prefetch_related(
                    Prefetch('options', queryset=QuestionOption.objects.all()),
                    Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
                ).filter(quizquestion__in=quiz_question_objects).all()
                
            except Quiz.DoesNotExist:
                messages.error(request, "ERROR : Invalid Quiz Id")
        elif form_type == "select_quiz":
            quiz_id = request.POST.get("select-quiz")
            selected_quiz_id = quiz_id
            try:

                quiz = get_object_or_404(Quiz, pk=quiz_id)
                quiz_question_objects = QuizQuestion.objects.filter(quiz = quiz)
                total_questions_added = quiz_question_objects.count()
                quiz_questions = Question.objects.select_related('type').prefetch_related(
                    Prefetch('options', queryset=QuestionOption.objects.all()),
                    Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
                ).filter(quizquestion__in=quiz_question_objects).all()
                
            except Quiz.DoesNotExist:
                messages.error(request, "ERROR : Invalid Quiz Id")
            selected_quiz_id = int(selected_quiz_id)
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
                quiz_questions = Question.objects.select_related('type').prefetch_related(
                    Prefetch('options', queryset=QuestionOption.objects.all()),
                    Prefetch('categoryquestionmap_set', queryset=CategoryQuestionMap.objects.select_related('category'))
                ).filter(quizquestion__in=quiz_question_objects).all()
                
            except Quiz.DoesNotExist:
                messages.error(request, "ERROR : Invalid Quiz Id")
            selected_quiz_id = int(selected_quiz_id)
    question_id_list = []
    for question in quiz_questions:
        question_id_list.append(question.id)

    return render(request, 'QuizCreator/modify_quiz_questions.html', {'quizzes': quizzes, 'categories' : categories, 'questions' : questions, 'quiz_questions': quiz_questions, 'total_questions_added' : total_questions_added, 'selected_quiz_id' : selected_quiz_id, 'question_id_list' : question_id_list})



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