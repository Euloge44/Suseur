from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, Category, MenuItem, MenuItemOption, MenuItemOptionChoice, Stock, Review, Promotion


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """Administration des restaurants"""
    
    list_display = ('name', 'owner', 'cuisine_type', 'is_active', 'is_verified', 'average_rating', 'created_at')
    list_filter = ('cuisine_type', 'is_active', 'is_verified', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    ordering = ('-created_at',)
    readonly_fields = ('average_rating', 'total_reviews', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('owner', 'name', 'description', 'cuisine_type')
        }),
        ('Contact et localisation', {
            'fields': ('address', 'phone', 'email', 'latitude', 'longitude')
        }),
        ('Images', {
            'fields': ('logo', 'cover_image')
        }),
        ('Horaires', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('Livraison', {
            'fields': ('delivery_fee', 'free_delivery_threshold', 'delivery_radius', 'estimated_delivery_time')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Statistiques', {
            'fields': ('average_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class MenuItemInline(admin.TabularInline):
    """Inline pour les articles de menu dans les catégories"""
    model = MenuItem
    extra = 0
    fields = ('name', 'price', 'is_available', 'is_featured')
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administration des catégories"""
    
    list_display = ('name', 'restaurant', 'is_active', 'order')
    list_filter = ('is_active', 'restaurant')
    search_fields = ('name', 'description', 'restaurant__name')
    ordering = ('restaurant', 'order', 'name')
    inlines = [MenuItemInline]


class MenuItemOptionChoiceInline(admin.TabularInline):
    """Inline pour les choix d'options"""
    model = MenuItemOptionChoice
    extra = 1


class MenuItemOptionInline(admin.TabularInline):
    """Inline pour les options des articles de menu"""
    model = MenuItemOption
    extra = 0


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Administration des articles de menu"""
    
    list_display = ('name', 'restaurant', 'category', 'price', 'is_available', 'is_featured', 'discount_percentage')
    list_filter = ('is_available', 'is_featured', 'is_vegetarian', 'is_vegan', 'is_spicy', 'restaurant', 'category')
    search_fields = ('name', 'description', 'restaurant__name')
    ordering = ('restaurant', 'category', 'name')
    readonly_fields = ('created_at', 'updated_at', 'discounted_price')
    inlines = [MenuItemOptionInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('restaurant', 'category', 'name', 'description', 'price', 'image')
        }),
        ('Détails', {
            'fields': ('calories', 'preparation_time')
        }),
        ('Options alimentaires', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_spicy')
        }),
        ('Disponibilité et promotion', {
            'fields': ('is_available', 'is_featured', 'discount_percentage', 'discounted_price')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(MenuItemOption)
class MenuItemOptionAdmin(admin.ModelAdmin):
    """Administration des options d'articles de menu"""
    
    list_display = ('name', 'menu_item', 'is_required')
    list_filter = ('is_required', 'menu_item__restaurant')
    search_fields = ('name', 'menu_item__name')
    inlines = [MenuItemOptionChoiceInline]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """Administration des stocks"""
    
    list_display = ('item_name', 'restaurant', 'current_quantity', 'minimum_threshold', 'is_low_stock', 'unit')
    list_filter = ('restaurant', 'low_stock_alert', 'unit')
    search_fields = ('item_name', 'restaurant__name')
    ordering = ('restaurant', 'item_name')
    readonly_fields = ('is_low_stock', 'created_at', 'updated_at')
    
    def is_low_stock(self, obj):
        """Afficher si le stock est faible"""
        if obj.is_low_stock:
            return format_html('<span style="color: red;">⚠️ Stock faible</span>')
        return format_html('<span style="color: green;">✅ Stock OK</span>')
    is_low_stock.short_description = 'État du stock'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Administration des avis"""
    
    list_display = ('restaurant', 'customer', 'rating', 'is_verified', 'created_at')
    list_filter = ('rating', 'is_verified', 'created_at', 'restaurant')
    search_fields = ('comment', 'restaurant__name', 'customer__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Avis', {
            'fields': ('restaurant', 'customer', 'rating', 'comment')
        }),
        ('Détails', {
            'fields': ('food_quality', 'delivery_time', 'customer_service')
        }),
        ('Statut', {
            'fields': ('is_verified',)
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Administration des promotions"""
    
    list_display = ('title', 'restaurant', 'promotion_type', 'discount_value', 'is_active', 'start_date', 'end_date')
    list_filter = ('promotion_type', 'is_active', 'start_date', 'end_date', 'restaurant')
    search_fields = ('title', 'description', 'restaurant__name')
    ordering = ('-start_date',)
    readonly_fields = ('current_uses', 'created_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('restaurant', 'title', 'description', 'promotion_type')
        }),
        ('Valeurs', {
            'fields': ('discount_value', 'minimum_order_amount')
        }),
        ('Période', {
            'fields': ('start_date', 'end_date')
        }),
        ('Limitations', {
            'fields': ('max_uses', 'current_uses')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
