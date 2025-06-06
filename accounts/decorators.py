from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_required(view_func):
    """Décorateur qui vérifie que l'utilisateur a le rôle admin"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
            raise PermissionDenied("Vous devez être administrateur pour accéder à cette page.")
        
        return view_func(request, *args, **kwargs)
    return wrapped_view

def user_or_admin_required(view_func):
    """Décorateur qui vérifie que l'utilisateur est connecté"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        return view_func(request, *args, **kwargs)
    return wrapped_view