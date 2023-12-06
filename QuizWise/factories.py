from QuizCreator.models import QuestionType, RadioButtonQuestion, CheckboxQuestion, FreeTextQuestion

class QuestionFactory:
    @staticmethod
    def create_question(question_type, question_text, answer, created_by, **kwargs):
        """
        Creates a question based on the specified question type.

        Parameters:
            - question_type (str): The type of the question ('RB' for RadioButton, 'CB' for Checkbox, 'FT' for FreeText).
            - question_text (str): The text of the question.
            - answer (str): The correct answer to the question.
            - created_by: The user who created the question.
            - **kwargs: Additional keyword arguments for creating the question.

        Returns:
            - RadioButtonQuestion, CheckboxQuestion, or FreeTextQuestion: The created question instance.

        Raises:
            - ValueError: If an invalid question type is provided.
        """
        question_type_instance = QuestionType.objects.get(type_code=question_type)
        if question_type == 'RB':
            return RadioButtonQuestion.objects.create(
                question=question_text,
                type=question_type_instance,
                answer=answer,
                created_by=created_by,
                **kwargs
            )
        elif question_type == 'CB':
            return CheckboxQuestion.objects.create(
                question=question_text,
                type=question_type_instance,
                answer=answer,
                created_by=created_by,
                **kwargs
            )
        elif question_type == 'FT':
            return FreeTextQuestion.objects.create(
                question=question_text,
                type=question_type_instance,
                answer=answer,
                created_by=created_by,
                **kwargs
            )
        else:
            raise ValueError("Invalid question type")