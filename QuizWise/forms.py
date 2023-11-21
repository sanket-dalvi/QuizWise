# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # Import your User model

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'contact']
