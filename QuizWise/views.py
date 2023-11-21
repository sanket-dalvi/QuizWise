# views.py
from django.shortcuts import render, redirect
from .forms import CreateUserForm

def index(request):
    return render(request, 'index.html') 

def create_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a success page or any other desired page
            return redirect('success_page')  # Replace 'success_page' with the URL name
    else:
        form = CreateUserForm()
    return render(request, 'create_user.html', {'form': form})
