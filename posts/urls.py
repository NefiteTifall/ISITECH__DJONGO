from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_extra
from . import api_views
from . import ai_views

app_name = 'posts'

# Configuration du router pour les API ViewSets
router = DefaultRouter()
router.register(r'api/articles', api_views.ArticleViewSet, basename='api-articles')
router.register(r'api/categories', api_views.CategoryViewSet, basename='api-categories')
router.register(r'api/tags', api_views.TagViewSet, basename='api-tags')

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    # path('explorer/', views.explorer, name='explorer'),
    path('recherche/', views_extra.search_articles, name='search'),
    
    # Gestion des articles
    path('ajouter/', views.ajouter_article, name='ajouter_article'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('article/<int:article_id>/reaction/', views.add_reaction, name='add_reaction'),
    path('article/<int:article_id>/delete/', views_extra.delete_article, name='delete_article'),
    
    # Actions utilisateur
    path('article/<int:article_id>/like/', views_extra.toggle_like, name='toggle_like'),
    path('article/<int:article_id>/bookmark/', views_extra.toggle_bookmark, name='toggle_bookmark'),
    
    # Commentaires
    path('article/<int:article_id>/comment/', views_extra.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views_extra.reply_comment, name='reply_comment'),
    
    # Catégories et tags
    path('categories/', views.categories_list, name='categories_list'),
    path('categorie/<slug:slug>/', views.category_detail, name='category_detail'),
    path('tags/', views_extra.tags_list, name='tags_list'),
    path('tag/<slug:slug>/', views_extra.tag_detail, name='tag_detail'),
    
    # Auteurs
    path('auteurs/', views.authors_list, name='authors_list'),
    path('auteur/<str:username>/', views.author_profile, name='author_profile'),
    
    # Séries d'articles (désactivé pour l'instant)
    # path('series/', views_extra.series_list, name='series_list'),
    # path('serie/<slug:slug>/', views_extra.series_detail, name='series_detail'),
    
    # Listes de lecture (désactivé pour l'instant)
    # path('listes-lecture/', views_extra.reading_lists, name='reading_lists'),
    # path('liste-lecture/<int:list_id>/', views_extra.reading_list_detail, name='reading_list_detail'),
    
    # Flux RSS et sitemap
    path('rss/', views_extra.latest_articles_feed, name='rss_feed'),
    path('sitemap.xml', views_extra.sitemap, name='sitemap'),
    
    # API REST
    path('', include(router.urls)),
    
    # APIs supplémentaires
    path('api/search/', views_extra.api_search, name='api_search'),
    path('api/popular/', views_extra.api_popular_articles, name='api_popular'),
    path('api/recent/', views_extra.api_recent_articles, name='api_recent'),
    path('api/stats/', views_extra.api_global_stats, name='api_stats'),
    
    # APIs utilitaires
    path('api/article/<int:article_id>/increment-view/', views_extra.increment_article_view, name='increment_view'),
    
    # APIs de génération d'IA
    path('ai/generate-article/', ai_views.GenerateArticleView.as_view(), name='ai_generate_article'),
    path('ai/generate-summary/', ai_views.GenerateSummaryView.as_view(), name='ai_generate_summary'),
    path('ai/generate-image/', ai_views.GenerateImageView.as_view(), name='ai_generate_image'),
    path('ai/generators/', ai_views.get_available_generators, name='ai_generators'),
    path('ai/diagnostic/', ai_views.ai_diagnostic, name='ai_diagnostic'),
]