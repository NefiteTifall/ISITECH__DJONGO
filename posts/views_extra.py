"""
Vues supplémentaires pour le blog - fonctionnalités avancées
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, Count
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.db import models

from .models import Article, Category, Tag, CommentArticle, Reaction
from .forms import SearchForm, CommentForm
# Fonctions utilitaires
def get_client_ip(request):
    """Obtenir l'IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def add_reaction_stats(articles, user_ip=None, user=None):
    """Ajouter les statistiques de réaction aux articles"""
    # Pour l'instant, on retourne les articles tels quels
    # Cette fonction peut être étendue plus tard
    return articles

def search_articles(request):
    """Vue de recherche simplifiée - Explorer"""
    articles = Article.objects.filter(statut='publié')
    
    # Récupération des paramètres GET
    query = request.GET.get('query', '').strip()
    category_id = request.GET.get('category', '')
    tag_ids = request.GET.getlist('tag')
    
    # Recherche textuelle
    if query:
        articles = articles.filter(
            Q(titre__icontains=query) |
            Q(contenu__icontains=query) |
            Q(resume__icontains=query)
        )
    
    # Filtre par catégorie
    if category_id:
        try:
            articles = articles.filter(categories__id=int(category_id))
        except (ValueError, TypeError):
            pass
    
    # Filtre par tags
    if tag_ids:
        try:
            tag_ids = [int(tag_id) for tag_id in tag_ids if tag_id.isdigit()]
            if tag_ids:
                articles = articles.filter(tags__id__in=tag_ids).distinct()
        except (ValueError, TypeError):
            pass
    
    # Tri par défaut
    articles = articles.order_by('-date_creation')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    articles_paginated = paginator.get_page(page)
    
    # Contexte
    categories = Category.objects.all().order_by('nom')
    tags = Tag.objects.all().order_by('nom')
    
    context = {
        'articles': articles_paginated,
        'categories': categories,
        'tags': tags,
        'query': query,
        'total_results': paginator.count,
    }
    
    return render(request, 'posts/explorer.html', context)

@login_required
@require_POST
def toggle_like(request, article_id):
    """Toggle le like d'un article"""
    article = get_object_or_404(Article, id=article_id, statut='publié')
    
    reaction, created = Reaction.objects.get_or_create(
        user=request.user,
        article=article,
        defaults={'reaction_type': 'like'}
    )
    
    if not created:
        reaction.delete()
        liked = False
        message = 'Article retiré de vos favoris.'
    else:
        liked = True
        message = 'Article ajouté à vos favoris !'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': article.get_reactions_count('like')
        })
    
    messages.success(request, message)
    return redirect('posts:article_detail', slug=article.slug)

@login_required
@require_POST
def toggle_bookmark(request, article_id):
    """Toggle le bookmark d'un article"""
    article = get_object_or_404(Article, id=article_id, statut='publié')
    
    reaction, created = Reaction.objects.get_or_create(
        user=request.user,
        article=article,
        reaction_type='bookmark'
    )
    
    if not created:
        reaction.delete()
        bookmarked = False
        message = 'Article retiré de vos signets.'
    else:
        bookmarked = True
        message = 'Article ajouté à vos signets !'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'bookmarked': bookmarked,
            'bookmarks_count': article.get_reactions_count('bookmark')
        })
    
    messages.success(request, message)
    return redirect('posts:article_detail', slug=article.slug)

@require_POST
def add_comment(request, article_id):
    """Ajouter un commentaire à un article"""
    article = get_object_or_404(Article, id=article_id, statut='publié')
    
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.ip_address = get_client_ip(request)
        
        if request.user.is_authenticated:
            comment.auteur = request.user.username
            comment.email = request.user.email
            comment.approuve = True
        
        comment.save()
        messages.success(request, 'Votre commentaire a été ajouté avec succès !')
    else:
        for error in form.errors.values():
            messages.error(request, error[0])
    
    return redirect('posts:article_detail', slug=article.slug)

@require_POST
def reply_comment(request, comment_id):
    """Répondre à un commentaire"""
    parent_comment = get_object_or_404(CommentArticle, id=comment_id, approuve=True)
    article = parent_comment.article
    
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.parent = parent_comment
        comment.ip_address = get_client_ip(request)
        
        if request.user.is_authenticated:
            comment.auteur = request.user.username
            comment.email = request.user.email
            comment.approuve = True
        
        comment.save()
        messages.success(request, 'Votre réponse a été ajoutée avec succès !')
    else:
        for error in form.errors.values():
            messages.error(request, error[0])
    
    return redirect('posts:article_detail', slug=article.slug)

def tags_list(request):
    """Liste tous les tags avec nombre d'articles"""
    tags = Tag.objects.annotate(
        articles_count=Count('articles', filter=Q(articles__statut='publié'))
    ).filter(articles_count__gt=0).order_by('-articles_count', 'nom')
    
    return render(request, 'posts/tags_list.html', {
        'tags': tags,
        'total_tags': tags.count()
    })

def tag_detail(request, slug):
    """Articles d'un tag spécifique"""
    tag = get_object_or_404(Tag, slug=slug)
    articles = Article.objects.filter(statut='publié', tags=tag).order_by('-date_creation')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    articles_paginated = paginator.get_page(page)
    
    return render(request, 'posts/tag_detail.html', {
        'tag': tag,
        'articles': articles_paginated
    })

def series_list(request):
    """Liste des séries d'articles"""
    series = ArticleSeries.objects.filter(is_public=True).select_related('auteur').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(series, 12)
    page = request.GET.get('page')
    series_paginated = paginator.get_page(page)
    
    return render(request, 'posts/series_list.html', {
        'series': series_paginated
    })

def series_detail(request, slug):
    """Détail d'une série d'articles"""
    series = get_object_or_404(ArticleSeries, slug=slug, is_public=True)
    articles = series.get_articles()
    
    return render(request, 'posts/series_detail.html', {
        'series': series,
        'articles': articles
    })

@login_required
def reading_lists(request):
    """Listes de lecture de l'utilisateur"""
    user_lists = ReadingList.objects.filter(user=request.user).order_by('-updated_at')
    
    return render(request, 'posts/reading_lists.html', {
        'reading_lists': user_lists
    })

@login_required
def reading_list_detail(request, list_id):
    """Détail d'une liste de lecture"""
    reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
    items = reading_list.items.select_related('article__auteur').order_by('-added_at')
    
    return render(request, 'posts/reading_list_detail.html', {
        'reading_list': reading_list,
        'items': items
    })

@login_required
@require_POST
def delete_article(request, article_id):
    """Supprimer un article"""
    article = get_object_or_404(Article, id=article_id, auteur=request.user)
    title = article.titre
    article.delete()
    messages.success(request, f'L\'article "{title}" a été supprimé avec succès.')
    return redirect('accounts:my_articles')

# APIs JSON simples
@require_GET
def api_search(request):
    """API de recherche simple"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Paramètre q requis'}, status=400)
    
    # Recherche simple pour SQLite
    articles = Article.objects.filter(
        statut='publié'
    ).filter(
        Q(titre__icontains=query) | Q(resume__icontains=query) | Q(contenu__icontains=query)
    )[:10]
    
    results = [{
        'id': article.id,
        'title': article.titre,
        'slug': article.slug,
        'excerpt': article.resume[:100] if article.resume else article.contenu[:100],
        'author': article.auteur.get_display_name(),
        'created_at': article.date_creation.isoformat(),
        'url': article.get_absolute_url()
    } for article in articles]
    
    return JsonResponse({'results': results})

@require_GET
def api_popular_articles(request):
    """API des articles populaires"""
    days = int(request.GET.get('days', 30))
    limit = int(request.GET.get('limit', 10))
    
    articles = Article.objects.popular(days=days)[:limit]
    
    results = [{
        'id': article.id,
        'title': article.titre,
        'slug': article.slug,
        'views': article.vues,
        'likes': article.get_reactions_count('like'),
        'author': article.auteur.get_display_name(),
        'url': article.get_absolute_url()
    } for article in articles]
    
    return JsonResponse({'articles': results})

@require_GET
def api_recent_articles(request):
    """API des articles récents"""
    limit = int(request.GET.get('limit', 10))
    
    articles = Article.objects.filter(statut='publié').order_by('-date_creation')[:limit]
    
    results = [{
        'id': article.id,
        'title': article.titre,
        'slug': article.slug,
        'created_at': article.date_creation.isoformat(),
        'author': article.auteur.get_display_name(),
        'url': article.get_absolute_url()
    } for article in articles]
    
    return JsonResponse({'articles': results})

@require_GET
def api_global_stats(request):
    """API des statistiques globales"""
    stats = {
        'total_articles': Article.objects.filter(statut='publié').count(),
        'total_authors': Article.objects.filter(statut='publié').values('auteur').distinct().count(),
        'total_views': Article.objects.filter(statut='publié').aggregate(total=models.Sum('vues'))['total'] or 0,
        'total_likes': Reaction.objects.filter(article__statut='publié', reaction_type='like').count(),
        'total_comments': CommentArticle.objects.filter(approuve=True).count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_tags': Tag.objects.annotate(
            articles_count=Count('articles', filter=Q(articles__statut='publié'))
        ).filter(articles_count__gt=0).count(),
    }
    
    return JsonResponse(stats)

@require_POST
def increment_article_view(request, article_id):
    """Incrémenter les vues d'un article via AJAX"""
    try:
        article = Article.objects.get(id=article_id, statut='publié')
        
        # Ne pas compter les vues de l'auteur
        if request.user.is_authenticated and request.user == article.auteur:
            return JsonResponse({'success': False, 'message': 'Auteur views not counted'})
        
        article.vues += 1
        article.save(update_fields=['vues'])
        return JsonResponse({'success': True, 'views': article.vues})
    
    except Article.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Article not found'}, status=404)

# Flux RSS
class LatestArticlesFeed(Feed):
    title = "Blog - Derniers Articles"
    link = "/rss/"
    description = "Les derniers articles de notre blog."
    
    def items(self):
        return Article.objects.filter(statut='publié').order_by('-date_creation')[:20]
    
    def item_title(self, item):
        return item.titre
    
    def item_description(self, item):
        return item.get_excerpt(200)
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.date_creation

latest_articles_feed = LatestArticlesFeed()

# Sitemap simple
def sitemap(request):
    """Génère un sitemap XML simple"""
    articles = Article.objects.filter(statut='publié').order_by('-date_modification')
    
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{}/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''.format(request.build_absolute_uri('/'))
    
    for article in articles:
        sitemap_xml += '''
    <url>
        <loc>{}</loc>
        <lastmod>{}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>'''.format(
            request.build_absolute_uri(article.get_absolute_url()),
            article.date_modification.strftime('%Y-%m-%d')
        )
    
    sitemap_xml += '''
</urlset>'''
    
    return HttpResponse(sitemap_xml, content_type='application/xml')

# Vues pour les tags
def tags_list(request):
    """Liste de tous les tags avec le nombre d'articles"""
    tags = Tag.objects.annotate(
        article_count=Count('articles', filter=Q(articles__statut='publié'))
    ).order_by('-article_count', 'nom')
    
    # Filtrer les tags qui ont au moins un article publié
    tags = tags.filter(article_count__gt=0)
    
    context = {
        'tags': tags,
        'total_tags': tags.count(),
    }
    return render(request, 'posts/tags_list.html', context)

def tag_detail(request, slug):
    """Détail d'un tag avec ses articles"""
    tag = get_object_or_404(Tag, slug=slug)
    
    # Articles du tag
    articles = Article.objects.filter(
        tags=tag,
        statut='publié'
    ).order_by('-date_creation')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Tags similaires (tags qui apparaissent souvent avec celui-ci)
    similar_tags = Tag.objects.filter(
        articles__in=tag.articles.filter(statut='publié')
    ).exclude(id=tag.id).annotate(
        common_count=Count('articles')
    ).order_by('-common_count')[:10]
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
        'articles': page_obj,
        'similar_tags': similar_tags,
        'total_articles': paginator.count,
    }
    return render(request, 'posts/tag_detail.html', context)