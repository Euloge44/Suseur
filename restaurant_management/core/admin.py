from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Notification, SystemConfiguration, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration des utilisateurs"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'phone', 'address', 'profile_picture', 'date_of_birth', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('email', 'first_name', 'last_name', 'role', 'phone')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Administration des notifications"""
    
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """Administration de la configuration système"""
    
    list_display = ('key', 'value_preview', 'description', 'updated_at')
    search_fields = ('key', 'description')
    ordering = ('key',)
    readonly_fields = ('created_at', 'updated_at')
    
    def value_preview(self, obj):
        """Aperçu de la valeur (tronquée)"""
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Valeur'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Administration du journal d'audit"""
    
    list_display = ('user', 'action', 'model_name', 'description_preview', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__username', 'description', 'model_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def description_preview(self, obj):
        """Aperçu de la description"""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        """Empêcher l'ajout manuel d'entrées d'audit"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Empêcher la modification des entrées d'audit"""
        return False
