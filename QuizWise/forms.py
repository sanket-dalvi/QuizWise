# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # Import your User model

class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('examinee', 'Examinee'),
        ('examiner', 'Examiner'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'contact', 'role']



class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
