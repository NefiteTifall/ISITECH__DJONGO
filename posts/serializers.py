from rest_framework import serializers
from .models import Article, Category, Tag, CommentArticle, Reaction
from accounts.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories"""
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'nom', 'slug', 'description', 'articles_count']
        read_only_fields = ['slug']
    
    def get_articles_count(self, obj):
        return obj.articles_category.filter(statut='publié').count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer pour les tags"""
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'nom', 'slug', 'articles_count']
        read_only_fields = ['slug']
    
    def get_articles_count(self, obj):
        return obj.articles.filter(statut='publié').count()


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer pour les auteurs"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'bio', 'avatar']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer pour les articles"""
    auteur = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Category.objects.all(), 
        write_only=True,
        source='categories'
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(), 
        write_only=True,
        source='tags'
    )
    reactions_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'titre', 'slug', 'resume', 'contenu', 'image',
            'auteur', 'categories', 'tags', 'category_ids', 'tag_ids',
            'statut', 'date_creation', 'date_modification',
            'vues', 'reactions_count', 'comments_count', 
            'is_liked', 'reading_time'
        ]
        read_only_fields = ['slug', 'auteur', 'vues', 'date_creation', 'date_modification']
    
    def get_reactions_count(self, obj):
        return {
            'like': obj.get_reactions_count('like'),
            'love': obj.get_reactions_count('love'),
            'insightful': obj.get_reactions_count('insightful'),
            'funny': obj.get_reactions_count('funny'),
        }
    
    def get_comments_count(self, obj):
        return obj.commentaires.filter(approuve=True).count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.reactions.filter(user=request.user, reaction_type='like').exists()
        return False
    
    def get_reading_time(self, obj):
        return obj.temps_lecture_minutes()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer pour les commentaires"""
    article_title = serializers.CharField(source='article.titre', read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CommentArticle
        fields = [
            'id', 'article', 'article_title', 'auteur', 'email',
            'contenu', 'date_creation', 'approuve',
            'parent', 'replies_count'
        ]
        read_only_fields = ['date_creation', 'approuve']
    
    def get_replies_count(self, obj):
        return obj.replies.count()


class ReactionSerializer(serializers.ModelSerializer):
    """Serializer pour les réactions"""
    article_title = serializers.CharField(source='article.titre', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Reaction
        fields = [
            'id', 'user', 'username', 'article', 'article_title',
            'reaction_type', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']