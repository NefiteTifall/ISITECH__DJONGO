from django.contrib import admin
from .models import Category, Article, CommentArticle, Tag, Reaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'date_creation', 'is_active')
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ('nom', 'description')
    list_filter = ('is_active', 'date_creation')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'date_creation')
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ('nom',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'statut', 'difficulty', 'is_featured', 'date_creation')
    list_filter = ('statut', 'difficulty', 'is_featured', 'allow_comments', 'date_creation', 'categories')
    search_fields = ('titre', 'contenu', 'resume')
    prepopulated_fields = {'slug': ('titre',)}
    filter_horizontal = ('categories', 'tags')
    readonly_fields = ('vues', 'date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'slug', 'auteur', 'resume')
        }),
        ('Contenu', {
            'fields': ('contenu', 'image', 'image_alt')
        }),
        ('Classification', {
            'fields': ('categories', 'tags', 'difficulty')
        }),
        ('Publication', {
            'fields': ('statut', 'is_featured', 'allow_comments')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('vues', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CommentArticle)
class CommentArticleAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'article', 'date_creation', 'approuve')
    list_filter = ('approuve', 'date_creation')
    search_fields = ('auteur', 'contenu', 'article__titre')
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(approuve=True)
    approve_comments.short_description = "Approuver les commentaires sélectionnés"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(approuve=False)
    disapprove_comments.short_description = "Désapprouver les commentaires sélectionnés"

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username', 'article__titre')
    readonly_fields = ('created_at',)