from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Article, CommentArticle, Category, Tag

User = get_user_model()

# Formulaire principal pour les articles (Markdown uniquement)
class ArticleForm(forms.ModelForm):
    contenu = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'markdown-editor',
            'placeholder': _('Écrivez votre article en Markdown...\n\n# Titre principal\n\n## Sous-titre\n\n**Texte en gras**\n\n*Texte en italique*\n\n```python\n# Code Python\nprint("Hello World")\n```\n\n- Liste à puces\n- Élément 2\n\n1. Liste numérotée\n2. Élément 2\n\n[Lien](https://example.com)\n\n![Image](url-image.jpg)')
        }),
        label=_("Contenu (Markdown)")
    )
    resume = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Résumé en Markdown (500 caractères max)...'),
            'maxlength': 500
        }),
        required=False,
        label=_("Résumé")
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text=_("Sélectionnez les tags appropriés pour votre article"),
        label=_("Tags")
    )
    
    class Meta:
        model = Article
        fields = [
            'titre', 'slug', 'resume', 'contenu', 'image', 'image_alt',
            'categories', 'tags', 'difficulty', 'statut', 'is_featured',
            'allow_comments', 'meta_title', 'meta_description'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Titre de l\'article'),
                'maxlength': 200
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL de l\'article (laissez vide pour générer automatiquement)')
            }),
            'resume': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Résumé de l\'article (500 caractères max)...'),
                'maxlength': 500
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Texte alternatif pour l\'image')
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Titre SEO (60 caractères max)'),
                'maxlength': 60
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Description SEO (160 caractères max)'),
                'maxlength': 160
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limiter les catégories actives
        self.fields['categories'].queryset = Category.objects.filter(is_active=True)
        
        # Définir une valeur par défaut pour difficulty si c'est un nouveau formulaire
        if not self.instance.pk:
            self.fields['difficulty'].initial = 'debutant'
        
        # Masquer les champs avancés pour les utilisateurs non-éditeurs
        if user and hasattr(user, 'is_editor_role') and not user.is_editor_role():
            self.fields.pop('is_featured', None)
            self.fields.pop('meta_title', None)
            self.fields.pop('meta_description', None)
    
    def clean_titre(self):
        titre = self.cleaned_data.get('titre')
        if not titre:
            raise ValidationError(_("Le titre est obligatoire."))
        if len(titre) < 5:
            raise ValidationError(_("Le titre doit contenir au moins 5 caractères."))
        return titre
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume and len(resume) < 20:
            raise ValidationError(_("Le résumé doit contenir au moins 20 caractères."))
        return resume
    
    def clean_contenu(self):
        contenu = self.cleaned_data.get('contenu')
        if not contenu:
            raise ValidationError(_("Le contenu est obligatoire."))
        
        # Validation du nombre de mots (en ignorant le Markdown)
        import re
        # Retirer les balises Markdown pour compter les vrais mots
        text_only = re.sub(r'[#*`_\-\[\]()]+', ' ', contenu)
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        word_count = len(text_only.split())
        
        if word_count < 50:
            raise ValidationError(_("L'article doit contenir au moins 50 mots."))
        return contenu
    
    def clean(self):
        cleaned_data = super().clean()
        slug = cleaned_data.get('slug')
        titre = cleaned_data.get('titre')
        
        # Si pas de slug fourni, on le génère à partir du titre
        if not slug and titre:
            from django.utils.text import slugify
            slug = slugify(titre)
            cleaned_data['slug'] = slug
        
        # Vérifier l'unicité du slug (sauf pour l'instance actuelle en mode édition)
        if slug:
            from .models import Article
            existing = Article.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(_("Un article avec ce slug existe déjà."))
        
        return cleaned_data

class CommentArticleForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=CommentArticle.objects.none(),
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = CommentArticle
        fields = ['auteur', 'email', 'contenu', 'parent']
        widgets = {
            'auteur': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre nom'),
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre email (ne sera pas publié)'),
                'required': False
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Partagez votre opinion sur cet article...'),
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        article = kwargs.pop('article', None)
        super().__init__(*args, **kwargs)
        
        # Si l'utilisateur est connecté, pré-remplir les champs
        if user and user.is_authenticated:
            self.fields['auteur'].initial = user.get_display_name()
            self.fields['email'].initial = user.email
            # Rendre les champs en lecture seule pour les utilisateurs connectés
            self.fields['auteur'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True
        
        # Configurer les commentaires parents possibles
        if article:
            self.fields['parent'].queryset = CommentArticle.objects.filter(
                article=article, 
                parent=None,  # Seulement les commentaires de niveau racine
                approuve=True
            )
    
    def clean_contenu(self):
        contenu = self.cleaned_data.get('contenu')
        if not contenu:
            raise ValidationError(_("Le commentaire ne peut pas être vide."))
        if len(contenu) < 5:
            raise ValidationError(_("Le commentaire doit contenir au moins 5 caractères."))
        if len(contenu) > 1000:
            raise ValidationError(_("Le commentaire ne peut pas dépasser 1000 caractères."))
        return contenu
    
    def clean_auteur(self):
        auteur = self.cleaned_data.get('auteur')
        if not auteur:
            raise ValidationError(_("Le nom est obligatoire."))
        return auteur

# Alias pour compatibilité
CommentForm = CommentArticleForm

class CategoryForm(forms.ModelForm):
    """Formulaire pour créer/modifier des catégories"""
    class Meta:
        model = Category
        fields = ['nom', 'slug', 'description', 'is_active']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nom de la catégorie')
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL de la catégorie (laissez vide pour générer automatiquement)')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Description de la catégorie')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class TagForm(forms.ModelForm):
    """Formulaire pour créer/modifier des tags"""
    class Meta:
        model = Tag
        fields = ['nom', 'slug']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nom du tag')
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL du tag (laissez vide pour générer automatiquement)')
            }),
        }

class SearchForm(forms.Form):
    """Formulaire de recherche avancée"""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Rechercher des articles...')
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_("Toutes les catégories"),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label=_("Tous les tags"),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    difficulty = forms.ChoiceField(
        choices=[('', _('Tous les niveaux'))] + Article.DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('recent', _('Plus récents')),
            ('popular', _('Plus populaires')),
            ('likes', _('Plus aimés')),
            ('views', _('Plus vus')),
        ],
        required=False,
        initial='recent',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )