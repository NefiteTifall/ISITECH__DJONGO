from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from .forms import SignUpForm, CustomAuthenticationForm
from posts.models import Article

User = get_user_model()

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, _('Bienvenue %(username)s!') % {'username': form.get_user().username})
        return super().form_valid(form)

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Le rôle par défaut est déjà défini dans le modèle User
            
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            authenticated_user = authenticate(username=email, password=password)
            if authenticated_user:
                login(request, authenticated_user)
            messages.success(request, _('Compte créé avec succès! Bienvenue %(username)s!') % {'username': user.username})
            return redirect('posts:home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Mise à jour du profil
        if 'update_profile' in request.POST:
            display_name = request.POST.get('display_name')
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            bio = request.POST.get('bio')
            website = request.POST.get('website')
            
            # Mise à jour du modèle User personnalisé
            request.user.username = username
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.display_name = display_name
            request.user.bio = bio
            request.user.website = website
            request.user.save()
            
            messages.success(request, _('Profil mis à jour avec succès!'))
            return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Votre mot de passe a été modifié avec succès!'))
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def my_articles_view(request):
    articles = Article.objects.filter(auteur=request.user).order_by('-date_creation')
    return render(request, 'accounts/my_articles.html', {'articles': articles})
