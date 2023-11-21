from functools import wraps
from django.contrib.auth.decorators import user_passes_test

def examiner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_examiner:
            # User is authenticated and is an Examiner
            return view_func(request, *args, **kwargs)
        else:
            # Redirect or handle unauthorized access
            # Example: redirect to a login page
            # return redirect('login')
            pass  # Handle unauthorized access as needed
    return _wrapped_view

def examinee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_examinee:
            # User is authenticated and is an Examinee
            return view_func(request, *args, **kwargs)
        else:
            # Redirect or handle unauthorized access
            # Example: redirect to a login page
            # return redirect('login')
            pass  # Handle unauthorized access as needed
    return _wrapped_view
