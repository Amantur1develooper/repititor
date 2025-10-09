from functools import wraps
from django.http import HttpResponseForbidden
from .models import UserProfile

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if hasattr(request.user, 'userprofile'):
                    if request.user.userprofile.role in allowed_roles:
                        return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()
        return _wrapped_view
    return decorator