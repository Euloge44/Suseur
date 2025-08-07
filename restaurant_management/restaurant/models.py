from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import User


class Restaurant(models.Model):
    """Modèle pour les restaurants"""
    
    CUISINE_TYPES = [
        ('african', 'Africaine'),
        ('asian', 'Asiatique'),
        ('european', 'Européenne'),
        ('american', 'Américaine'),
        ('mediterranean', 'Méditerranéenne'),
        ('fast_food', 'Fast Food'),
        ('pizza', 'Pizza'),
        ('dessert', 'Dessert'),
    ]
    
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_profile')
    name = models.CharField(max_length=200)
    description = models.TextField()
    cuisine_type = models.CharField(max_length=20, choices=CUISINE_TYPES)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='restaurant_covers/', blank=True, null=True)
    
    # Géolocalisation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Horaires
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    
    # Statut et évaluations
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Livraison
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    free_delivery_threshold = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    delivery_radius = models.PositiveIntegerField(default=5)  # en km
    estimated_delivery_time = models.PositiveIntegerField(default=30)  # en minutes
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Category(models.Model):
    """Catégories de plats"""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"


class MenuItem(models.Model):
    """Plats du menu"""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    
    # Informations nutritionnelles
    calories = models.PositiveIntegerField(blank=True, null=True)
    preparation_time = models.PositiveIntegerField(default=15)  # en minutes
    
    # Options
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    
    # Promotion
    is_featured = models.BooleanField(default=False)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"
    
    @property
    def discounted_price(self):
        if self.discount_percentage > 0:
            return self.price * (1 - self.discount_percentage / 100)
        return self.price


class MenuItemOption(models.Model):
    """Options pour les plats (taille, suppléments, etc.)"""
    
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)  # Ex: "Taille", "Supplément"
    is_required = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.name}"


class MenuItemOptionChoice(models.Model):
    """Choix pour les options de plats"""
    
    option = models.ForeignKey(MenuItemOption, on_delete=models.CASCADE, related_name='choices')
    name = models.CharField(max_length=100)  # Ex: "Grande", "Fromage"
    additional_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.option.name} - {self.name}"


class Stock(models.Model):
    """Gestion des stocks"""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='stocks')
    item_name = models.CharField(max_length=200)
    current_quantity = models.PositiveIntegerField(default=0)
    minimum_threshold = models.PositiveIntegerField(default=10)
    unit = models.CharField(max_length=20, default='piece')  # piece, kg, litre, etc.
    
    # Alertes
    low_stock_alert = models.BooleanField(default=True)
    last_restocked = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['item_name']
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.item_name}"
    
    @property
    def is_low_stock(self):
        return self.current_quantity <= self.minimum_threshold


class Review(models.Model):
    """Avis clients sur les restaurants"""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    
    # Détails de l'avis
    food_quality = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    delivery_time = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    customer_service = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['restaurant', 'customer']
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.customer.username} - {self.rating}★"


class Promotion(models.Model):
    """Promotions et offres spéciales"""
    
    PROMOTION_TYPES = [
        ('percentage', 'Pourcentage'),
        ('fixed_amount', 'Montant fixe'),
        ('free_delivery', 'Livraison gratuite'),
        ('buy_one_get_one', 'Achetez-en un, obtenez-en un gratuit'),
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='promotions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    
    # Valeurs de promotion
    discount_value = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    minimum_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Période de validité
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Limitations
    max_uses = models.PositiveIntegerField(blank=True, null=True)
    current_uses = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.title}"
