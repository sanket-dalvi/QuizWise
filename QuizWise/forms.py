# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User 

class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('examinee', 'Examinee'),
        ('examiner', 'Examiner'),
    )
    
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    contact = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Enter your contact number'}))
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        required=True,
        widget=forms.Select(attrs={'class': 'fancy-select'})
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'contact', 'role']



class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
