from django import template
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.timesince import timesince
import re
import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc

register = template.Library()

@register.filter
def reading_time(content):
    """Calcule le temps de lecture estimé en minutes"""
    if not content:
        return 1
    
    # Nettoyer le HTML et compter les mots
    clean_text = re.sub(r'<[^>]+>', '', str(content))
    word_count = len(clean_text.split())
    
    # 200 mots par minute en moyenne
    reading_time_minutes = max(1, round(word_count / 200))
    
    if reading_time_minutes == 1:
        return "1 min"
    return f"{reading_time_minutes} min"

@register.filter
def highlight_search(text, search_query):
    """Surligne les termes de recherche dans le texte"""
    if not search_query or not text:
        return text
    
    highlighted = re.sub(
        f'({re.escape(search_query)})',
        r'<mark class="bg-yellow-200">\1</mark>',
        str(text),
        flags=re.IGNORECASE
    )
    return mark_safe(highlighted)

@register.filter
def relative_time(value):
    """Affiche le temps relatif de manière conviviale"""
    if not value:
        return ""
    
    now = timezone.now()
    diff = now - value
    
    if diff.days == 0:
        if diff.seconds < 3600:  # Moins d'1 heure
            minutes = diff.seconds // 60
            if minutes < 1:
                return "À l'instant"
            elif minutes == 1:
                return "Il y a 1 minute"
            else:
                return f"Il y a {minutes} minutes"
        else:  # Moins d'1 jour
            hours = diff.seconds // 3600
            if hours == 1:
                return "Il y a 1 heure"
            else:
                return f"Il y a {hours} heures"
    elif diff.days == 1:
        return "Hier"
    elif diff.days < 7:
        return f"Il y a {diff.days} jours"
    else:
        return value.strftime("%d %B %Y")

@register.filter
def truncate_html(value, length=100):
    """Tronque le contenu HTML en gardant les balises"""
    if not value:
        return ""
    
    # Nettoyer le HTML
    clean_text = re.sub(r'<[^>]+>', '', str(value))
    
    if len(clean_text) <= length:
        return value
    
    truncated = clean_text[:length] + "..."
    return truncated

@register.filter
def format_number(value):
    """Formate les nombres pour l'affichage (1000 -> 1k)"""
    if not value:
        return "0"
    
    try:
        num = int(value)
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}k"
        else:
            return str(num)
    except (ValueError, TypeError):
        return value

@register.simple_tag
def url_replace(request, field, value):
    """Remplace ou ajoute un paramètre dans l'URL"""
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

@register.inclusion_tag('posts/includes/pagination.html')
def render_pagination(page_obj, request):
    """Rend la pagination"""
    return {
        'page_obj': page_obj,
        'request': request,
    }

@register.inclusion_tag('posts/components/article_card.html', takes_context=True)
def render_article_card(context, article, show_reactions=True, show_stats=True, show_status=False, show_actions=False):
    """Rend une carte d'article avec des options configurables"""
    return {
        'article': article,
        'show_reactions': show_reactions,
        'show_stats': show_stats,
        'show_status': show_status,
        'show_actions': show_actions,
        'user_reactions': context.get('user_reactions', {}),
        'user': context.get('user'),
    }

@register.inclusion_tag('posts/components/article_card_home.html', takes_context=True)
def render_article_card_home(context, article):
    """Rend une carte d'article spécialisée pour la page d'accueil avec toutes les fonctionnalités"""
    return {
        'article': article,
        'user_reactions': context.get('user_reactions', {}),
        'user': context.get('user'),
    }

@register.simple_tag
def get_popular_categories(limit=5):
    """Récupère les catégories populaires"""
    from posts.models import Category
    from django.db import models
    return Category.objects.annotate(
        articles_count=models.Count('articles_category', filter=models.Q(articles_category__status='published'))
    ).filter(articles_count__gt=0).order_by('-articles_count')[:limit]

@register.filter
def markdown_to_html(text):
    """Convertit le texte Markdown en HTML"""
    if not text:
        return ""
    
    # Configuration des extensions Markdown
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.codehilite',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
            },
            'markdown.extensions.toc': {
                'permalink': True,
            }
        }
    )
    
    html = md.convert(text)
    return mark_safe(html)