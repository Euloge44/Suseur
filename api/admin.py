from django.contrib import admin
from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour Restaurant"""
    list_display = ['name', 'phone', 'email', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Contact', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Horaires et capacité', {
            'fields': ('opening_time', 'closing_time', 'capacity')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )