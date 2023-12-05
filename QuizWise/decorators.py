from functools import wraps
import logging

def log_view(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.info(f"View function '{func.__name__}' called.")
        return func(request, *args, **kwargs)
    return wrapper