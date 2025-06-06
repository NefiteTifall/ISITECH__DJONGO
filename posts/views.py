from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.http import JsonResponse

from .models import Article, CommentArticle, Category, Tag
from .forms import ArticleForm, CommentArticleForm

User = get_user_model()

def home(request):
    # Récupérer tous les articles publiés
    articles = Article.objects.filter(statut='publié').order_by('-date_creation')
    
    # Pagination 
    paginator = Paginator(articles, 6)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    context = {
        'articles': articles,
    }
    return render(request, 'posts/home.html', context)

@login_required
def ajouter_article(request):
    if request.method == 'POST':
        # Déterminer le statut selon le bouton cliqué
        if 'publish' in request.POST:
            statut = 'publié'
        elif 'save_draft' in request.POST:
            statut = 'brouillon'
        else:
            statut = request.POST.get('statut', 'brouillon')
        
        # Créer une copie modifiable des données POST
        post_data = request.POST.copy()
        post_data['statut'] = statut
        
        # S'assurer que difficulty a une valeur valide
        if 'difficulty' not in post_data or not post_data['difficulty']:
            post_data['difficulty'] = 'debutant'
        
        form = ArticleForm(post_data, request.FILES, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user  # assigner l'auteur
            
            # générer le slug si il n'y en a pas
            if not article.slug:
                article.slug = slugify(article.titre)
            
            article.save()
            form.save_m2m()  # important pour les many to many
            
            action = "publié" if statut == 'publié' else "sauvegardé comme brouillon"
            messages.success(request, f'Article {action} avec succès!')
            return redirect('posts:home')
        else:
            messages.error(request, 'Erreur dans le formulaire')
            # Debug: afficher les erreurs
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ArticleForm(user=request.user)
    
    return render(request, 'posts/ajouter_article.html', {'form': form})

def article_detail(request, slug):
    """Vue de détail d'un article"""
    article = get_object_or_404(Article, slug=slug, statut='publié')
    
    # Incrémenter les vues
    article.vues += 1
    article.save(update_fields=['vues'])
    
    # Commentaires approuvés
    commentaires = article.commentaires.filter(approuve=True).order_by('date_creation')
    
    # Articles similaires
    articles_similaires = Article.objects.filter(
        statut='publié',
        categories__in=article.categories.all()
    ).exclude(id=article.id).distinct()[:3]
    
    context = {
        'article': article,
        'commentaires': commentaires,
        'articles_similaires': articles_similaires,
        'form': CommentArticleForm(),
    }
    return render(request, 'posts/article_detail.html', context)

def categories_list(request):
    """Liste des catégories"""
    categories = Category.objects.filter(is_active=True).order_by('nom')
    return render(request, 'posts/categories.html', {'categories': categories})

def category_detail(request, slug):
    """Détail d'une catégorie"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    articles = Article.objects.filter(statut='publié', categories=category).order_by('-date_creation')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'posts/category_detail.html', context)

def add_reaction(request, article_id):
    """Ajouter une réaction à un article"""
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour réagir.")
        return redirect('accounts:login')
    
    article = get_object_or_404(Article, id=article_id, statut='publié')
    reaction_type = request.POST.get('reaction_type', 'like')
    
    # Toggle de la réaction
    reaction, created = Reaction.objects.get_or_create(
        user=request.user,
        article=article,
        reaction_type=reaction_type
    )
    
    if not created:
        reaction.delete()
        message = "Réaction supprimée"
    else:
        message = "Réaction ajoutée"
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'liked': created,
            'count': article.get_reactions_count(reaction_type)
        })
    
    messages.success(request, message)
    return redirect('posts:article_detail', slug=article.slug)

@login_required
def edit_article(request, article_id):
    """Éditer un article existant"""
    article = get_object_or_404(Article, id=article_id, auteur=request.user)
    
    if request.method == 'POST':
        # Déterminer le statut selon le bouton cliqué
        if 'publish' in request.POST:
            statut = 'publié'
        elif 'save_draft' in request.POST:
            statut = 'brouillon'
        else:
            statut = request.POST.get('statut', article.statut)
        
        # Créer une copie modifiable des données POST
        post_data = request.POST.copy()
        post_data['statut'] = statut
        
        # S'assurer que difficulty a une valeur valide
        if 'difficulty' not in post_data or not post_data['difficulty']:
            post_data['difficulty'] = article.difficulty or 'debutant'
        
        form = ArticleForm(post_data, request.FILES, instance=article, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            
            # générer le slug si il n'y en a pas
            if not article.slug:
                article.slug = slugify(article.titre)
            
            article.save()
            form.save_m2m()
            
            action = "publié" if statut == 'publié' else "sauvegardé"
            messages.success(request, f'Article {action} avec succès!')
            return redirect('posts:article_detail', slug=article.slug)
        else:
            messages.error(request, 'Erreur dans le formulaire')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ArticleForm(instance=article, user=request.user)
    
    context = {
        'form': form,
        'article': article,
        'editing': True
    }
    return render(request, 'posts/ajouter_article.html', context)

def authors_list(request):
    """Vue pour afficher la liste des auteurs"""
    from django.db.models import Count, Sum, Q
    
    # Filtrer les utilisateurs qui ont publié au moins un article
    authors = User.objects.filter(
        articles__statut='publié'
    ).annotate(
        articles_count=Count('articles', filter=Q(articles__statut='publié')),
        total_views=Sum('articles__vues', filter=Q(articles__statut='publié')),
        total_reactions=Count('articles__reactions', filter=Q(articles__statut='publié'), distinct=True)
    ).filter(articles_count__gt=0).order_by('-articles_count', '-total_views').distinct()
    
    # Pagination
    paginator = Paginator(authors, 12)  # 12 auteurs par page
    page = request.GET.get('page')
    authors_paginated = paginator.get_page(page)
    
    context = {
        'authors': authors_paginated,
        'total_authors': authors.count(),
    }
    
    return render(request, 'posts/authors_list.html', context)

def author_profile(request, username):
    """Vue pour afficher le profil d'un auteur"""
    from django.db.models import Count, Sum, Avg
    
    author = get_object_or_404(User, username=username)
    
    # Articles publiés de l'auteur
    articles = Article.objects.filter(
        auteur=author, 
        statut='publié'
    ).select_related('auteur').prefetch_related('categories', 'tags').order_by('-date_creation')
    
    # Statistiques de l'auteur
    stats = Article.objects.filter(auteur=author, statut='publié').aggregate(
        total_articles=Count('id'),
        total_views=Sum('vues'),
        avg_views=Avg('vues'),
        total_likes=Count('reactions', filter=Q(reactions__reaction_type='like'))
    )
    
    # Pagination des articles
    paginator = Paginator(articles, 9)
    page = request.GET.get('page')
    articles_paginated = paginator.get_page(page)
    
    # Vérifier si l'utilisateur actuel suit cet auteur
    is_following = False
    if request.user.is_authenticated:
        is_following = author.followers.filter(id=request.user.id).exists()
    
    context = {
        'author': author,
        'articles': articles_paginated,
        'stats': stats,
        'is_following': is_following,
        'followers_count': author.followers.count(),
    }
    
    return render(request, 'posts/author_profile.html', context)