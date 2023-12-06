from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User 
from .constants import (
    EMAIL_PLACEHOLDER,
    USERNAME_PLACEHOLDER,
    PASSWORD_PLACEHOLDER,
    CONFIRM_PASSWORD_PLACEHOLDER,
    FIRST_NAME_PLACEHOLDER,
    LAST_NAME_PLACEHOLDER,
    CONTACT_PLACEHOLDER,
    USERNAME_LABEL,
    PASSWORD_LABEL,
)

class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration.

    Fields:
        - email
        - username
        - password1
        - password2
        - first_name
        - last_name
        - contact
        - role
    """
    ROLE_CHOICES = (
        ('examinee', 'Examinee'),
        ('examiner', 'Examiner'),
    )
    
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'placeholder': EMAIL_PLACEHOLDER}))
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': USERNAME_PLACEHOLDER}))
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'placeholder': PASSWORD_PLACEHOLDER}))
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'placeholder': CONFIRM_PASSWORD_PLACEHOLDER}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': FIRST_NAME_PLACEHOLDER}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': LAST_NAME_PLACEHOLDER}))
    contact = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': CONTACT_PLACEHOLDER}))
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        required=True,
        widget=forms.Select(attrs={'class': 'fancy-select'})
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'contact', 'role']

class UserLoginForm(forms.Form):
    """
    Form for user login.

    Fields:
        - username
        - password
    """
    username = forms.CharField(max_length=150, label=USERNAME_LABEL)
    password = forms.CharField(widget=forms.PasswordInput, label=PASSWORD_LABEL)
