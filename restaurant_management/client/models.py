from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import User
from restaurant.models import Restaurant, MenuItem, MenuItemOptionChoice


class CustomerProfile(models.Model):
    """Profil étendu pour les clients"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    preferred_cuisine_types = models.ManyToManyField('restaurant.Restaurant', through='PreferredCuisine', blank=True)
    
    # Préférences de livraison
    default_delivery_address = models.TextField(blank=True)
    delivery_instructions = models.TextField(blank=True)
    
    # Programme de fidélité
    loyalty_points = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Préférences de notification
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"


class PreferredCuisine(models.Model):
    """Table intermédiaire pour les cuisines préférées"""
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    preference_level = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    class Meta:
        unique_together = ['customer', 'restaurant']


class Order(models.Model):
    """Commandes des clients"""
    
    ORDER_STATUS = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('preparing', 'En préparation'),
        ('ready', 'Prête'),
        ('out_for_delivery', 'En cours de livraison'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('failed', 'Échouée'),
        ('refunded', 'Remboursée'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    
    # Statut
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Montants
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Livraison
    delivery_address = models.TextField()
    delivery_instructions = models.TextField(blank=True)
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)
    actual_delivery_time = models.DateTimeField(blank=True, null=True)
    
    # Programme de fidélité
    loyalty_points_earned = models.PositiveIntegerField(default=0)
    loyalty_points_used = models.PositiveIntegerField(default=0)
    
    # Métadonnées
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commande #{self.order_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Articles d'une commande"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderItemOption(models.Model):
    """Options sélectionnées pour un article de commande"""
    
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='selected_options')
    option_choice = models.ForeignKey(MenuItemOptionChoice, on_delete=models.CASCADE)
    additional_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.order_item} - {self.option_choice.name}"


class Payment(models.Model):
    """Paiements des commandes"""
    
    PAYMENT_METHODS = [
        ('tmoney', 'T-Money'),
        ('flooz', 'Flooz'),
        ('card', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('cash', 'Espèces'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Détails du paiement
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_gateway_response = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Paiement {self.order.order_number} - {self.get_payment_method_display()}"


class Cart(models.Model):
    """Panier d'achat"""
    
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Panier de {self.customer.username}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Articles du panier"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class CartItemOption(models.Model):
    """Options sélectionnées pour un article du panier"""
    
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name='selected_options')
    option_choice = models.ForeignKey(MenuItemOptionChoice, on_delete=models.CASCADE)
    additional_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.cart_item} - {self.option_choice.name}"


class Favorite(models.Model):
    """Restaurants favoris des clients"""
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'restaurant']
    
    def __str__(self):
        return f"{self.customer.username} ♥ {self.restaurant.name}"


class LoyaltyTransaction(models.Model):
    """Transactions du programme de fidélité"""
    
    TRANSACTION_TYPES = [
        ('earned', 'Points gagnés'),
        ('redeemed', 'Points utilisés'),
        ('expired', 'Points expirés'),
        ('bonus', 'Points bonus'),
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='loyalty_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()  # Peut être négatif pour les utilisations
    description = models.CharField(max_length=200)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.user.username} - {self.points} points ({self.get_transaction_type_display()})"


class Address(models.Model):
    """Adresses sauvegardées des clients"""
    
    ADDRESS_TYPES = [
        ('home', 'Domicile'),
        ('work', 'Travail'),
        ('other', 'Autre'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Géolocalisation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Instructions de livraison
    delivery_instructions = models.TextField(blank=True)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', 'label']
    
    def __str__(self):
        return f"{self.customer.username} - {self.label}"
