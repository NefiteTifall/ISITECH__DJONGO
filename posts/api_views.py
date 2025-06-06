from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Article, Category, Tag, CommentArticle, Reaction
from .serializers import (
    ArticleSerializer, CategorySerializer, TagSerializer, 
    CommentSerializer, ReactionSerializer
)


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des articles via l'API
    """
    queryset = Article.objects.filter(statut='publié').order_by('-date_creation')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['titre', 'contenu', 'resume']
    filterset_fields = ['statut', 'categories', 'tags', 'auteur']
    ordering_fields = ['date_creation', 'date_modification', 'titre']
    
    def get_queryset(self):
        """Personnaliser le queryset selon l'utilisateur"""
        queryset = super().get_queryset()
        
        # Si l'utilisateur est authentifié, montrer ses brouillons
        if self.request.user.is_authenticated:
            queryset = Article.objects.filter(
                Q(statut='publié') | Q(auteur=self.request.user)
            ).distinct()
        
        # Filtrage par catégorie
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        # Filtrage par tag
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__slug=tag)
            
        return queryset.order_by('-date_creation')
    
    def perform_create(self, serializer):
        """Définir l'auteur automatiquement lors de la création"""
        serializer.save(auteur=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_like(self, request, pk=None):
        """Liker/Unliker un article"""
        article = self.get_object()
        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            article=article,
            defaults={'reaction_type': 'like'}
        )
        
        if not created:
            reaction.delete()
            liked = False
        else:
            liked = True
        
        return Response({
            'liked': liked,
            'likes_count': article.get_reactions_count('like')
        })
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Obtenir des articles similaires"""
        article = self.get_object()
        similar_articles = Article.get_similar_articles(article)[:5]
        serializer = self.get_serializer(similar_articles, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les catégories (lecture seule)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def articles(self, request, slug=None):
        """Obtenir tous les articles d'une catégorie"""
        category = self.get_object()
        articles = Article.objects.filter(
            categories=category,
            statut='publié'
        ).order_by('-date_creation')
        
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = ArticleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les tags (lecture seule)
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def articles(self, request, slug=None):
        """Obtenir tous les articles d'un tag"""
        tag = self.get_object()
        articles = Article.objects.filter(
            tags=tag,
            statut='publié'
        ).order_by('-date_creation')
        
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = ArticleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des commentaires
    """
    queryset = CommentArticle.objects.filter(approuve=True).order_by('-date_creation')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtrer les commentaires par article si spécifié"""
        queryset = super().get_queryset()
        article_id = self.request.query_params.get('article', None)
        
        if article_id:
            queryset = queryset.filter(article_id=article_id)
            
        return queryset
    
    def perform_create(self, serializer):
        """Approuver automatiquement si l'utilisateur est authentifié"""
        if self.request.user.is_authenticated:
            serializer.save(
                auteur=self.request.user.username,
                email=self.request.user.email,
                approuve=True
            )
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        """Approuver un commentaire (pour les modérateurs)"""
        comment = self.get_object()
        
        if not request.user.can_moderate_comments():
            return Response(
                {'detail': 'Vous n\'avez pas la permission de modérer les commentaires.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment.approuve = True
        comment.save()
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data)


class ReactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des réactions
    """
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les réactions de l'utilisateur connecté"""
        return super().get_queryset().filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Définir l'utilisateur automatiquement"""
        serializer.save(user=self.request.user)