from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

User = get_user_model()

class Category(models.Model):
    nom = models.CharField(max_length=100, unique=True, default='Sans nom', verbose_name='Nom')
    slug = models.SlugField(unique=True, max_length=120, verbose_name='URL')
    description = models.TextField(max_length=500, blank=True, verbose_name='Description')
    is_active = models.BooleanField(default=True, verbose_name='Catégorie active')
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date de création')
    
    class Meta:
        ordering = ['nom']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom
    
    def get_absolute_url(self):
        return reverse('posts:category_detail', kwargs={'slug': self.slug})

class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True, default='tag')
    slug = models.SlugField(unique=True, max_length=60)
    date_creation = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['nom']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom
    
    def get_absolute_url(self):
        return reverse('posts:tag_detail', kwargs={'slug': self.slug})
    

class ArticleManager(models.Manager):
    def published(self):
        return self.filter(statut='publié')
    
    def draft(self):
        return self.filter(statut='brouillon')
    
    def popular(self, days=30):
        """Articles populaires basés sur les vues et réactions"""
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        return self.filter(
            statut='publié',
            date_creation__gte=since
        ).order_by('-vues')

class Article(models.Model):
    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publié', 'Publié'),
        ('archivé', 'Archivé'),
        ('programmé', 'Programmé'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('debutant', 'Débutant'),
        ('intermediaire', 'Intermédiaire'),
        ('avance', 'Avancé'),
        ('expert', 'Expert'),
    ]
    
    # Champs principaux
    titre = models.CharField(max_length=200, verbose_name='Titre')
    slug = models.SlugField(unique=True, max_length=220, blank=True, verbose_name='URL')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name='Auteur')
    contenu = models.TextField(verbose_name='Contenu')
    resume = models.TextField(max_length=500, blank=True, verbose_name='Résumé')
    
    # Image et métadonnées
    image = models.ImageField(upload_to='articles/%Y/%m/', blank=True, null=True, verbose_name='Image de couverture')
    image_alt = models.CharField(max_length=200, blank=True, verbose_name='Texte alternatif de l\'image')
    
    # Relations
    categories = models.ManyToManyField(Category, blank=True, related_name='articles_category', verbose_name='Catégories')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name='Tags')
    
    # Statut et paramètres
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon', verbose_name='Statut')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='debutant', verbose_name='Difficulté')
    is_featured = models.BooleanField(default=False, verbose_name='Article en vedette')
    allow_comments = models.BooleanField(default=True, verbose_name='Autoriser les commentaires')
    
    # Statistiques
    vues = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True, verbose_name='Titre SEO')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Description SEO')
    
    # Dates
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date de création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    
    # Manager personnalisé
    objects = ArticleManager()
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
            # Vérifier l'unicité 
            original_slug = self.slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.titre
    
    def get_absolute_url(self):
        return reverse('posts:article_detail', kwargs={'slug': self.slug})
    
    def get_reactions_count(self, reaction_type):
        """Obtenir le nombre de réactions d'un type donné"""
        return self.reactions.filter(reaction_type=reaction_type).count()
    
    def temps_lecture_minutes(self):
        """Calculer le temps de lecture estimé en minutes"""
        mots = len(self.contenu.split())
        # Moyenne de 200 mots par minute
        minutes = max(1, round(mots / 200))
        return minutes

class CommentArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.CharField(max_length=100)
    email = models.EmailField()
    contenu = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    approuve = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['date_creation']
    
    def __str__(self):
        return f'Commentaire de {self.auteur} sur {self.article.titre}'


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'J\'aime'),
        ('love', 'J\'adore'),
        ('insightful', 'Instructif'),
        ('funny', 'Drôle'),
        ('bookmark', 'Signet'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'article', 'reaction_type')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_reaction_type_display()} - {self.article.titre}'

