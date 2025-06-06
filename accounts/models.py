from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('reader', _('Lecteur')),
        ('author', _('Auteur')),
        ('editor', _('Éditeur')),
        ('admin', _('Administrateur')),
    )
    
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader', verbose_name=_("Rôle"))
    display_name = models.CharField(max_length=100, blank=True, verbose_name=_("Nom d'affichage"))
    bio = models.TextField(max_length=500, blank=True, verbose_name=_("Biographie"))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_("Avatar"))
    website = models.URLField(blank=True, verbose_name=_("Site web"))
    twitter = models.CharField(max_length=50, blank=True, verbose_name=_("Twitter"))
    linkedin = models.CharField(max_length=50, blank=True, verbose_name=_("LinkedIn"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Localisation"))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_("Date de naissance"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone"))
    
    # Privacy settings
    show_email = models.BooleanField(default=False, verbose_name=_("Afficher l'email publiquement"))
    email_notifications = models.BooleanField(default=True, verbose_name=_("Recevoir les notifications par email"))
    
    # Timestamps
    email_verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Email vérifié le"))
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Dernière IP de connexion"))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        permissions = [
            ('can_moderate_comments', _('Peut modérer les commentaires')),
            ('can_publish_articles', _('Peut publier des articles')),
            ('can_manage_categories', _('Peut gérer les catégories')),
            ('can_view_analytics', _('Peut voir les statistiques')),
        ]
    
    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.username
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})
    
    def is_admin_role(self):
        return self.role == 'admin'
    
    def is_editor_role(self):
        return self.role in ['editor', 'admin']
    
    def is_author_role(self):
        return self.role in ['author', 'editor', 'admin']
    
    def is_reader_role(self):
        return self.role == 'reader'
    
    def can_publish_articles(self):
        return self.role in ['author', 'editor', 'admin']
    
    def can_moderate_comments(self):
        return self.role in ['editor', 'admin']
    
    def can_manage_users(self):
        return self.role == 'admin'
    
    def get_display_name(self):
        return self.display_name or self.username
    
    def get_articles_count(self):
        return self.articles.filter(statut='publié').count()
    
    def get_total_views(self):
        return sum(article.vues for article in self.articles.filter(statut='publié'))
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username
    
    def __str__(self):
        return f"{self.get_display_name()} ({self.email})"

# Ancien modèle supprimé - maintenant intégré dans le modèle User personnalisé

class UserSession(models.Model):
    """Modèle pour tracker les sessions utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name=_("Utilisateur"))
    session_key = models.CharField(max_length=40, unique=True, verbose_name=_("Clé de session"))
    ip_address = models.GenericIPAddressField(verbose_name=_("Adresse IP"))
    user_agent = models.TextField(verbose_name=_("User Agent"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Créée le"))
    last_activity = models.DateTimeField(auto_now=True, verbose_name=_("Dernière activité"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    class Meta:
        verbose_name = _("Session utilisateur")
        verbose_name_plural = _("Sessions utilisateur")
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Session de {self.user.username} - {self.ip_address}"

class UserActivity(models.Model):
    """Modèle pour tracker l'activité utilisateur"""
    ACTION_CHOICES = [
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('view_article', _('Vue d\'article')),
        ('like_article', _('Like d\'article')),
        ('comment', _('Commentaire')),
        ('bookmark', _('Ajout signet')),
        ('profile_update', _('Mise à jour profil')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', verbose_name=_("Utilisateur"))
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name=_("Action"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    ip_address = models.GenericIPAddressField(verbose_name=_("Adresse IP"))
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_("Horodatage"))
    
    class Meta:
        verbose_name = _("Activité utilisateur")
        verbose_name_plural = _("Activités utilisateur")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"
