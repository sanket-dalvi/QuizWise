from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, UserLoginForm
from .auth_decorator  import examiner_required
from django.contrib import messages
from .email_utils import EmailSender
from django.contrib import messages
from .models import User, PasswordReset
from django.db.models import Q
import uuid
from django.utils import timezone
from django.utils.crypto import get_random_string
from .decorators import log_view

@log_view
def index(request):
    return render(request, "index.html")

@log_view
def register_user(request):
    """
    View function for user registration.
    Handles the submission of the registration form, creates a new user, and assigns the appropriate role.

    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            user = form.save(commit=False)
            # Assign role based on the selected option
            if role == 'examinee':
                user.is_examinee = True
            elif role == 'examiner':
                user.is_examiner = True
            user.save()
            return redirect('login')
        
    else:
        form = UserRegistrationForm(initial={'email': request.GET.get("email")})
    return render(request, 'register.html', {'form': form})

@log_view
def user_login(request):
    """
    View function for user login.
    Handles the submission of the login form, authenticates the user, and redirects based on their role.

    """
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_examiner:
                    return redirect("examiner/home")
                else:
                    return redirect("examinee/home")  
            else:
                messages.error(request, 'Invalid username or password') 

    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

@log_view
def user_logout(request):
    logout(request)
    return redirect('login') 

@log_view
@examiner_required
def examiner_test(request):
    return render(request, 'success_page.html')


@log_view
def unauthorized(request):
    return render(request, "unauthorized.html")

@log_view
def forgot(request):
    if request.method == "POST":
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        email = request.POST['email'].strip()
        user = User.objects.filter(Q(first_name__iexact=first_name) & Q(last_name__iexact=last_name) & Q(email__iexact=email)).first()

        if user:
            # Generate a unique token for password reset
            token = uuid.uuid4().hex  # Using UUID for generating a secure token
            # Store the token in the PasswordReset model
            PasswordReset.objects.create(user=user, token=token) 
            # Send an email to the user with the reset link containing the token
            reset_link = f"http://localhost:8000/reset_password/?token={token}"  # Replace with your domain
            email_sender = EmailSender()
            email_sender.send_custom_email("QuizWise - Password Reset", f"Please follow this link to reset your password: {reset_link}", [email])
            messages.success(request, "Reset link sent successfully.")\
            
        else:
            messages.error(request, "User not found. Please provide correct information.")
    return render(request, "forgot.html")


@log_view
def reset_password(request):
    """
    View function for resetting the user password.
    Handles the submission of the password reset form and processes the reset link.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        # Check if the entered passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('forgot')

        try:
            # Verify the provided email, OTP, and timestamp
            reset_data = PasswordReset.objects.get(user__email=email, otp=otp, created_at__gte=timezone.now()-timezone.timedelta(minutes=15))
            user = reset_data.user
            user.set_password(new_password)
            user.save()
            reset_data.delete()  
            messages.success(request, 'Password reset successfully.')
            return redirect('login')
        except PasswordReset.DoesNotExist:
            messages.error(request, 'Invalid email or OTP. Please try again.')
            return redirect('forgot')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('forgot')
    else:
        # Handle the GET request to generate and send an OTP for password reset
        token = request.GET.get("token").strip()
        reset_link_data = PasswordReset.objects.filter(token=token).first()
        if reset_link_data:
            # Generate a new OTP and send it to the user via email
            otp = get_random_string(length=6, allowed_chars='1234567890')
            reset_link_data.otp = otp
            reset_link_data.save()
            email_sender = EmailSender()
            email_sender.send_custom_email("QuizWise - Password Reset - OTP", f"Please use this one time passcode to reset your password: {otp}", [reset_link_data.user.email])
            messages.success(request, "OTP Sent Successfully.")
        else:
            messages.error(request, "Invalid Rest Link URL. Please Generate it Again.")
        return render(request, 'reset.html')
