from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django.forms.models import BaseInlineFormSet

from Instructors.models import (Answers, Challenges, CorrectAnswers,
                                DynamicQuestions, Prompts, Questions, Skills,
                                StaticQuestions)


class MultipleChoiceQuestionsFormSet(BaseInlineFormSet):
    pass

class MultipleAnswerQuestionsFormSet(BaseInlineFormSet):
    pass

class EssayFormSet(BaseInlineFormSet):
    pass

class MultipleChoiceQuestionsForm(ModelForm):
    preview = forms.CharField(max_length=200, help_text="Please enter the category name.")
    instructorNotes = forms.CharField(max_length=300, help_text="Please enter the category name.")
    difficulty = forms.CharField(max_length=50, help_text="Please enter the category name.")
    author = forms.CharField(max_length=100, help_text="Please enter the category name.")
    
    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Questions   
        # What fields do we want to include in our form?
        # This way we don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them...
        # Here, we are hiding the foreign key.
        fields = ('preview', 'instructorNotes', 'difficulty', 'author')



class MultipleAnswerQuestionsForm(ModelForm):
    preview = forms.CharField(max_length=200, help_text="Preview of the question.")
    instructorNotes = forms.CharField(max_length=300, help_text="Notes for the instructor")
    difficulty = forms.CharField(max_length=50, help_text="The difficulty level of the question")
    author = forms.CharField(max_length=100, help_text="The creator of the question")
    
    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Questions
        fields = ('preview', 'instructorNotes', 'difficulty', 'author')

class TrueFalseQuestionsForm(forms.ModelForm):
    preview = forms.CharField(max_length=200, help_text="Preview of the question.")
    instructorNotes = forms.CharField(max_length=300, help_text="Notes for the instructor")
    difficulty = forms.CharField(max_length=50, help_text="The difficulty level of the question")
    author = forms.CharField(max_length=100, help_text="The creator of the question")

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Questions
        fields = ('preview', 'instructorNotes', 'difficulty', 'author')
        
class ParsonsForm(forms.ModelForm):
    preview = forms.CharField(max_length=200, help_text="Preview of the question.")
    instructorNotes = forms.CharField(max_length=300, help_text="Notes for the instructor")
    difficulty = forms.CharField(max_length=50, help_text="The difficulty level of the question")
    author = forms.CharField(max_length=100, help_text="The creator of the question")

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Questions
        fields = ('preview', 'instructorNotes', 'difficulty', 'author')

