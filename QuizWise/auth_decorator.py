from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def examiner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated and has examiner privileges
        if request.user.is_authenticated and request.user.is_examiner:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to the 'unauthorized' page if not authorized
            return redirect("unauthorized") 
    return _wrapped_view

def examinee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated and has examinee privileges
        if request.user.is_authenticated and request.user.is_examinee:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to the 'unauthorized' page if not authorized
            return redirect("unauthorized")
    return _wrapped_view
