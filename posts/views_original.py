from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.utils.text import slugify
from django.utils import timezone

from .models import Article, CommentArticle, Category, Tag
from .forms import ArticleForm, CommentArticleForm

User = get_user_model()

def home(request):
    articles = Article.objects.filter(status='published').order_by('-date_creation')
    
    # Pagination simple
    paginator = Paginator(articles, 6)
    page = request.GET.get('page')
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    return render(request, 'posts/home.html', {
        'articles': articles,
    })

@login_required
def ajouter_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            
            # Générer le slug
            if not article.slug:
                article.slug = slugify(article.titre)
            
            article.save()
            form.save_m2m()
            
            messages.success(request, 'Article créé avec succès!')
            return redirect('posts:home')
    else:
        form = ArticleForm()
    
    return render(request, 'posts/ajouter_article.html', {'form': form})

def article_detail(request, slug):
    # Permettre aux auteurs de voir leurs propres brouillons
    if request.user.is_authenticated:
        article = get_object_or_404(Article, slug=slug)
        if article.status != 'published' and article.auteur != request.user:
            messages.error(request, _("Cet article n'est pas encore publié."))
            return redirect('posts:home')
    else:
        article = get_object_or_404(Article, slug=slug, status='published')
    
    commentaires = article.commentaires.filter(approuve=True)
    
    # Obtenir l'IP du visiteur
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    user_ip = get_client_ip(request)
    
    # Obtenir toutes les réactions de l'utilisateur pour cet article
    user_reactions = ReactionArticle.objects.filter(article=article, ip_address=user_ip)
    user_reaction_types = list(user_reactions.values_list('type_reaction', flat=True))
    
    # Compter les réactions par type
    reaction_counts = {}
    for choice in ReactionArticle.REACTION_CHOICES:
        reaction_type = choice[0]
        count = article.reactions.filter(type_reaction=reaction_type).count()
        reaction_counts[reaction_type] = count
    
    # Traitement du formulaire de commentaire
    if request.method == 'POST':
        form = CommentArticleForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.save()
            messages.success(request, _('Votre commentaire a été ajouté avec succès!'))
            return redirect('posts:article_detail', slug=article.slug)
    else:
        form = CommentArticleForm()
    
    context = {
        'article': article,
        'commentaires': commentaires,
        'form': form,
        'user_reaction_types': user_reaction_types,
        'reaction_counts': reaction_counts,
        'reaction_choices': ReactionArticle.REACTION_CHOICES,
    }
    
    return render(request, 'posts/article_detail.html', context)

def article_detail_by_id(request, article_id):
    """Vue pour accéder à un article par son ID - redirige vers l'URL avec slug"""
    article = get_object_or_404(Article, id=article_id)
    return redirect('posts:article_detail', slug=article.slug)

def add_reaction(request, article_id):
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        reaction_type = request.POST.get('reaction_type')
        
        # Obtenir l'IP du visiteur
        def get_client_ip(request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        
        user_ip = get_client_ip(request)
        
        # Vérifier si l'utilisateur a déjà cette réaction spécifique
        try:
            existing_reaction = ReactionArticle.objects.get(
                article=article, 
                ip_address=user_ip, 
                type_reaction=reaction_type
            )
            # Si la réaction existe déjà, la supprimer (toggle)
            existing_reaction.delete()
            action = 'removed'
            messages.success(request, _('Réaction %(reaction)s supprimée!') % {'reaction': dict(ReactionArticle.REACTION_CHOICES)[reaction_type]})
        except ReactionArticle.DoesNotExist:
            # Créer une nouvelle réaction
            ReactionArticle.objects.create(
                article=article,
                type_reaction=reaction_type,
                ip_address=user_ip
            )
            action = 'added'
            messages.success(request, _('Réaction %(reaction)s ajoutée!') % {'reaction': dict(ReactionArticle.REACTION_CHOICES)[reaction_type]})
        
        # Si c'est une requête AJAX, retourner JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Compter les nouvelles réactions
            reaction_counts = {}
            for choice in ReactionArticle.REACTION_CHOICES:
                reaction_type_count = choice[0]
                count = article.reactions.filter(type_reaction=reaction_type_count).count()
                reaction_counts[reaction_type_count] = count
            
            return JsonResponse({
                'success': True,
                'action': action,
                'reaction_counts': reaction_counts
            })
        else:
            # Redirection normale pour les formulaires classiques
            return redirect('posts:article_detail', slug=article.slug)

def categories_list(request):
    """Liste toutes les catégories avec le nombre d'articles"""
    categories = Category.objects.all()
    categories_with_count = []
    
    for category in categories:
        article_count = category.articles_category.filter(status='published').count()
        categories_with_count.append({
            'category': category,
            'article_count': article_count
        })
    
    return render(request, 'posts/categories.html', {
        'categories_with_count': categories_with_count
    })

def category_detail(request, slug):
    """Affiche les articles d'une catégorie spécifique"""
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles_category.filter(status='published').order_by('-date_creation')
    
    # Ajouter les données de réactions pour chaque article
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    user_ip = get_client_ip(request)
    
    articles_with_reactions = []
    for article in articles:
        # Compter les réactions par type
        reaction_stats = {}
        total_reactions = 0
        for choice in ReactionArticle.REACTION_CHOICES:
            reaction_type = choice[0]
            count = article.reactions.filter(type_reaction=reaction_type).count()
            if count > 0:
                reaction_stats[reaction_type] = {
                    'count': count,
                    'emoji': choice[1].split(' ')[0]
                }
                total_reactions += count
        
        user_reactions = ReactionArticle.objects.filter(article=article, ip_address=user_ip)
        user_reaction_types = list(user_reactions.values_list('type_reaction', flat=True))
        
        article.reaction_stats = reaction_stats
        article.total_reactions = total_reactions
        article.user_reaction_types = user_reaction_types
        articles_with_reactions.append(article)
    
    return render(request, 'posts/category_detail.html', {
        'category': category,
        'articles': articles_with_reactions
    })

@login_required
def toggle_article_status(request, article_id):
    """Publie ou dépublie un article"""
    article = get_object_or_404(Article, id=article_id, auteur=request.user)
    
    if article.status == 'published':
        article.unpublish()
        messages.success(request, _('Article remis en brouillon.'))
    else:
        article.publish()
        messages.success(request, _('Article publié avec succès!'))
    
    # Rediriger vers la page d'où vient l'utilisateur
    return redirect(request.META.get('HTTP_REFERER', 'accounts:my_articles'))

@login_required
def edit_article(request, article_id):
    """Éditer un article existant"""
    article = get_object_or_404(Article, id=article_id, auteur=request.user)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            
            # Générer le slug si vide ou par défaut
            if not article.slug or article.slug == 'article-slug':
                base_slug = slugify(article.titre)
                slug = base_slug
                num = 1
                # S'assurer que le slug est unique (exclure l'article actuel)
                while Article.objects.filter(slug=slug).exclude(id=article.id).exists():
                    slug = f"{base_slug}-{num}"
                    num += 1
                article.slug = slug
            
            # Déterminer le statut selon le bouton cliqué
            if 'save_draft' in request.POST:
                article.status = 'draft'
                messages.success(request, _('Article enregistré comme brouillon!'))
            elif 'publish' in request.POST:
                article.status = 'published'
                messages.success(request, _('Article publié avec succès!'))
            
            article.save()
            form.save_m2m()
            
            if article.status == 'draft':
                return redirect('accounts:my_articles')
            else:
                return redirect('posts:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'posts/ajouter_article.html', {
        'form': form,
        'article': article,
        'is_edit': True
    })

@login_required
def ajouter_article_simple(request):
    """Version simplifiée pour tester les boutons"""
    if request.method == 'POST':
        # Traitement simple du formulaire
        titre = request.POST.get('titre', '').strip()
        resume = request.POST.get('resume', '').strip()
        contenu = request.POST.get('contenu', '').strip()
        
        if titre and contenu:
            try:
                article = Article.objects.create(
                    titre=titre,
                    slug=slugify(titre),
                    auteur=request.user,
                    contenu=contenu,
                    resume=resume,
                    status='published' if 'publish' in request.POST else 'draft',
                    difficulty='beginner',
                    allow_comments=True,
                    is_featured=False
                )
                messages.success(request, f"Article '{article.titre}' créé avec succès !")
                return redirect('posts:article_detail', slug=article.slug)
            except Exception as e:
                messages.error(request, f"Erreur lors de la création : {str(e)}")
        else:
            messages.error(request, "Titre et contenu sont obligatoires")
    
    return render(request, 'posts/ajouter_article_simple.html')

def explorer(request):
    # Récupérer les paramètres de recherche et filtres
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    tag_filter = request.GET.get('tag', '')
    sort_by = request.GET.get('sort', 'recent')
    
    # Construire la requête de base
    articles = Article.objects.filter(status='published').select_related('auteur').prefetch_related('categories', 'tags')
    
    # Filtrage par recherche PostgreSQL
    if search_query:
        articles = articles.annotate(
            search=SearchVector('titre', 'contenu', 'resume', config='french'),
            rank=SearchRank(SearchVector('titre', 'contenu', 'resume', config='french'), SearchQuery(search_query, config='french'))
        ).filter(search=SearchQuery(search_query, config='french')).order_by('-rank', '-date_creation')
    
    # Filtrage par catégorie
    if category_filter:
        articles = articles.filter(categories__id=category_filter)
    
    # Filtrage par tag
    if tag_filter:
        articles = articles.filter(tags__id=tag_filter)
    
    # Tri
    if not search_query:  # Si pas de recherche, appliquer le tri normal
        if sort_by == 'popular':
            articles = articles.order_by('-vues', '-likes_count')
        elif sort_by == 'likes':
            articles = articles.order_by('-likes_count', '-date_creation')
        else:  # recent par défaut
            articles = articles.order_by('-date_creation')
    
    # Obtenir l'IP du visiteur pour vérifier ses réactions
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    user_ip = get_client_ip(request)
    
    # Pagination
    paginator = Paginator(articles, 12)  # 12 articles par page
    page = request.GET.get('page')
    
    try:
        articles_paginated = paginator.page(page)
    except PageNotAnInteger:
        articles_paginated = paginator.page(1)
    except EmptyPage:
        articles_paginated = paginator.page(paginator.num_pages)
    
    # Ajouter les statistiques de réactions pour chaque article
    articles_with_reactions = []
    for article in articles_paginated:
        # Compter les réactions par type
        reaction_stats = {}
        total_reactions = 0
        for choice in ReactionArticle.REACTION_CHOICES:
            reaction_type = choice[0]
            count = article.reactions.filter(type_reaction=reaction_type).count()
            if count > 0:
                reaction_stats[reaction_type] = {
                    'count': count,
                    'emoji': choice[1].split(' ')[0]
                }
                total_reactions += count
        
        # Obtenir les réactions de l'utilisateur pour cet article
        user_reactions = ReactionArticle.objects.filter(article=article, ip_address=user_ip)
        user_reaction_types = list(user_reactions.values_list('type_reaction', flat=True))
        
        article.reaction_stats = reaction_stats
        article.total_reactions = total_reactions
        article.user_reaction_types = user_reaction_types
        articles_with_reactions.append(article)
    
    # Mettre à jour l'objet page avec nos articles enrichis
    articles_paginated.object_list = articles_with_reactions
    
    # Obtenir toutes les catégories et tags pour les filtres
    categories = Category.objects.all()
    popular_tags = Tag.get_popular_tags(limit=10)
    
    return render(request, 'posts/explorer.html', {
        'articles': articles_paginated,
        'categories': categories,
        'popular_tags': popular_tags,
        'search_query': search_query,
        'category_filter': category_filter,
        'tag_filter': tag_filter,
        'sort_by': sort_by,
    })


def authors_list(request):
    """Vue pour afficher la liste des auteurs"""
    # Filtrer les utilisateurs qui ont publié au moins un article
    authors = User.objects.filter(
        articles__status='published'
    ).annotate(
        articles_count=Count('articles', filter=Q(articles__status='published')),
        total_views=Sum('articles__vues', filter=Q(articles__status='published')),
        total_reactions=Count('articles__reactions', filter=Q(articles__status='published'))
    ).filter(articles_count__gt=0).order_by('-articles_count', '-total_views')
    
    # Pagination
    paginator = Paginator(authors, 12)  # 12 auteurs par page
    page = request.GET.get('page')
    
    try:
        authors_paginated = paginator.page(page)
    except PageNotAnInteger:
        authors_paginated = paginator.page(1)
    except EmptyPage:
        authors_paginated = paginator.page(paginator.num_pages)
    
    return render(request, 'posts/authors_list.html', {
        'authors': authors_paginated,
    })


def author_profile(request, username):
    """Vue pour afficher le profil d'un auteur"""
    author = get_object_or_404(User, username=username)
    
    # Articles publiés de l'auteur
    articles = Article.objects.filter(
        auteur=author, 
        status='published'
    ).select_related('auteur').prefetch_related('categories', 'tags').order_by('-published_at')
    
    # Statistiques de l'auteur
    stats = {
        'articles_count': articles.count(),
        'total_views': articles.aggregate(total=Sum('vues'))['total'] or 0,
        'total_reactions': ReactionArticle.objects.filter(article__auteur=author).count(),
        'total_comments': CommentArticle.objects.filter(article__auteur=author, approuve=True).count(),
    }
    
    # Articles récents (derniers 5) - triés par date de publication
    recent_articles = articles.order_by('-published_at')[:5]
    
    # Articles les plus populaires (par vues) - triés par vues
    popular_articles = articles.order_by('-vues')[:5]
    
    return render(request, 'posts/author_profile.html', {
        'author': author,
        'stats': stats,
        'recent_articles': recent_articles,
        'popular_articles': popular_articles,
    })
