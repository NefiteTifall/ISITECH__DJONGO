from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ArticleViewSet, CategoryViewSet, TagViewSet,
    CommentViewSet, ReactionViewSet
)

# Créer le router et enregistrer les ViewSets
router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'reactions', ReactionViewSet)

# URLs de l'API
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),  # URLs d'authentification DRF
]