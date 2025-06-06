from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .views import CustomLoginView, signup_view, profile_view, change_password_view, my_articles_view

app_name = 'accounts'

urlpatterns = [
    path('connexion/', CustomLoginView.as_view(), name='login'),
    path('deconnexion/', LogoutView.as_view(next_page='/'), name='logout'),
    path('inscription/', signup_view, name='signup'),
    path('profil/', profile_view, name='profile'),
    path('profil/changer-mot-de-passe/', change_password_view, name='change_password'),
    path('mes-articles/', my_articles_view, name='my_articles'),
    
    # Reset password URLs
    path('reinitialiser-mot-de-passe/', 
         PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/reinitialiser-mot-de-passe/envoye/'
         ), 
         name='password_reset'),
    path('reinitialiser-mot-de-passe/envoye/', 
         PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reinitialiser-mot-de-passe/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reinitialiser-mot-de-passe/termine/'
         ), 
         name='password_reset_confirm'),
    path('reinitialiser-mot-de-passe/termine/', 
         PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]