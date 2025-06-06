from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class RolePermissionMiddleware(MiddlewareMixin):
    """
    Middleware pour gérer les permissions basées sur les rôles
    """
    
    AUTHOR_REQUIRED_URLS = [
        '/posts/ajouter/',
        '/dashboard/',
    ]
    
    EDITOR_REQUIRED_URLS = [
        '/admin/moderate/',
    ]
    
    ADMIN_REQUIRED_URLS = [
        '/admin/users/',
    ]
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        
        path = request.path
        user = request.user
        
        # Vérifier les permissions pour les URLs d'auteur
        if any(path.startswith(url) for url in self.AUTHOR_REQUIRED_URLS):
            if not user.can_publish_articles():
                messages.error(request, "Vous devez être auteur pour accéder à cette page.")
                return redirect('posts:home')
        
        # Vérifier les permissions pour les URLs d'éditeur
        if any(path.startswith(url) for url in self.EDITOR_REQUIRED_URLS):
            if not user.can_moderate_comments():
                messages.error(request, "Vous devez être éditeur pour accéder à cette page.")
                return redirect('posts:home')
        
        # Vérifier les permissions pour les URLs d'admin
        if any(path.startswith(url) for url in self.ADMIN_REQUIRED_URLS):
            if not user.can_manage_users():
                messages.error(request, "Vous devez être administrateur pour accéder à cette page.")
                return redirect('posts:home')
        
        return None