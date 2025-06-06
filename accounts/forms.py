from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full pl-10 pr-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-[#da3e44] focus:bg-white focus:ring-2 focus:ring-red-200 text-gray-700 transition duration-200',
        'placeholder': _('votre@email.com')
    }))
    display_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full pl-10 pr-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-[#da3e44] focus:bg-white focus:ring-2 focus:ring-red-200 text-gray-700 transition duration-200',
        'placeholder': _('Nom d\'affichage (optionnel)')
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'display_name', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-[#da3e44] focus:bg-white focus:ring-2 focus:ring-red-200 text-gray-700 transition duration-200',
            'placeholder': _('Choisissez un nom d\'utilisateur')
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-[#da3e44] focus:bg-white focus:ring-2 focus:ring-red-200 text-gray-700 transition duration-200',
            'placeholder': _('Créez un mot de passe sécurisé')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-[#da3e44] focus:bg-white focus:ring-2 focus:ring-red-200 text-gray-700 transition duration-200',
            'placeholder': _('Confirmez votre mot de passe')
        })
        self.fields['display_name'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-[#da3e44] focus:bg-white focus:ring-2 focus:ring-red-200 text-gray-700 transition duration-200',
            'placeholder': _('Nom d\'affichage (optionnel)')
        })

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-[#da3e44] focus:bg-white focus:ring-2 focus:ring-red-200 text-gray-700 transition duration-200',
            'placeholder': _('Nom d\'utilisateur ou email'),
            'autocomplete': 'username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-[#da3e44] focus:bg-white focus:ring-2 focus:ring-red-200 text-gray-700 transition duration-200',
            'placeholder': _('Mot de passe'),
            'autocomplete': 'current-password'
        })
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # Si ça ressemble à un email, utiliser directement l'email pour l'authentification
            if '@' in username:
                self.user_cache = authenticate(self.request, username=username, password=password)
            else:
                # Si c'est un nom d'utilisateur, trouver l'email correspondant
                try:
                    user_obj = User.objects.get(username=username)
                    self.user_cache = authenticate(self.request, username=user_obj.email, password=password)
                except User.DoesNotExist:
                    self.user_cache = None
            
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data