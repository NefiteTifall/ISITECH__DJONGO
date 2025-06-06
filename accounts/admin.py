from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserSession, UserActivity

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Ajout des champs personnalisés au UserAdmin par défaut
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations personnelles', {
            'fields': (
                'display_name', 'bio', 'avatar', 'website', 'twitter', 'linkedin',
                'location', 'birth_date', 'phone'
            )
        }),
        ('Rôle et permissions', {
            'fields': ('role',)
        }),
        ('Confidentialité', {
            'fields': ('show_email', 'email_notifications')
        }),
        ('Métadonnées', {
            'fields': ('email_verified_at', 'last_login_ip'),
            'classes': ('collapse',)
        }),
    )
    
    list_display = (
        'username', 'email', 'display_name', 'role', 'is_staff', 
        'is_active', 'date_joined', 'get_articles_count'
    )
    list_filter = BaseUserAdmin.list_filter + ('role', 'email_verified_at')
    search_fields = BaseUserAdmin.search_fields + ('display_name', 'bio')
    
    def get_articles_count(self, obj):
        return obj.get_articles_count()
    get_articles_count.short_description = 'Articles publiés'

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'created_at', 'last_activity', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('session_key', 'created_at', 'last_activity')
    
    def has_add_permission(self, request):
        return False

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('user', 'action', 'description', 'ip_address', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
