from QuizCreator.models import QuestionType, RadioButtonQuestion, CheckboxQuestion, FreeTextQuestion

class QuestionFactory:
    @staticmethod
    def create_question(question_type, question_text, answer, created_by, **kwargs):
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