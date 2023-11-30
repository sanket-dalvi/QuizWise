def user_first_name(request):
    return {
        'user_first_name': request.user.first_name if request.user.is_authenticated else ''
    }
