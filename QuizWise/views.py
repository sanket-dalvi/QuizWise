# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, UserLoginForm
from .auth_decorator  import examinee_required, examiner_required
from django.contrib import messages


def index(request):
    return render(request, "index.html")

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            user = form.save(commit=False)
            if role == 'examinee':
                user.is_examinee = True
            elif role == 'examiner':
                user.is_examiner = True
            user.save()
            # Redirect to a success page
            return render(request, 'success_page.html')  
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username)
            print(password)
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return render(request, 'success_page.html')  
            else:
                messages.error(request, 'Invalid username or password') 
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    # Redirect to a specific page after logout 
    return redirect('login') 

@examiner_required
def examiner_test(request):
    return render(request, 'success_page.html')


def unauthorized(request):
    return render(request, "unauthorized.html")

def forget(request):
    return render(request, "forget.html")
