from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import User
from client.models import Order


class DeliveryPersonProfile(models.Model):
    """Profil étendu pour les livreurs"""
    
    VEHICLE_TYPES = [
        ('bike', 'Vélo'),
        ('scooter', 'Scooter'),
        ('motorcycle', 'Moto'),
        ('car', 'Voiture'),
        ('foot', 'À pied'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('busy', 'Occupé'),
        ('offline', 'Hors ligne'),
        ('on_break', 'En pause'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_profile')
    
    # Informations personnelles
    license_number = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    vehicle_registration = models.CharField(max_length=50, blank=True)
    
    # Documents
    identity_document = models.ImageField(upload_to='delivery_docs/', blank=True, null=True)
    driving_license = models.ImageField(upload_to='delivery_docs/', blank=True, null=True)
    vehicle_insurance = models.ImageField(upload_to='delivery_docs/', blank=True, null=True)
    
    # Statut et disponibilité
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Localisation
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    last_location_update = models.DateTimeField(blank=True, null=True)
    
    # Zone de livraison
    delivery_radius = models.PositiveIntegerField(default=10)  # en km
    
    # Statistiques
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Préférences
    max_orders_per_hour = models.PositiveIntegerField(default=4)
    preferred_working_hours_start = models.TimeField(blank=True, null=True)
    preferred_working_hours_end = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Livreur {self.user.username}"
    
    @property
    def success_rate(self):
        if self.total_deliveries > 0:
            return (self.successful_deliveries / self.total_deliveries) * 100
        return 0


class Delivery(models.Model):
    """Livraisons assignées aux livreurs"""
    
    DELIVERY_STATUS = [
        ('assigned', 'Assignée'),
        ('accepted', 'Acceptée'),
        ('picked_up', 'Récupérée'),
        ('in_transit', 'En transit'),
        ('delivered', 'Livrée'),
        ('failed', 'Échec'),
        ('cancelled', 'Annulée'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_person = models.ForeignKey(DeliveryPersonProfile, on_delete=models.CASCADE, related_name='deliveries')
    
    # Statut et timing
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    picked_up_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    # Estimation et réalité
    estimated_pickup_time = models.DateTimeField()
    estimated_delivery_time = models.DateTimeField()
    actual_pickup_time = models.DateTimeField(blank=True, null=True)
    actual_delivery_time = models.DateTimeField(blank=True, null=True)
    
    # Distance et temps
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    travel_time_minutes = models.PositiveIntegerField(blank=True, null=True)
    
    # Paiement livreur
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    tip_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)  # %
    earnings = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Notes et problèmes
    pickup_notes = models.TextField(blank=True)
    delivery_notes = models.TextField(blank=True)
    issue_reported = models.TextField(blank=True)
    
    # Preuve de livraison
    delivery_photo = models.ImageField(upload_to='delivery_proofs/', blank=True, null=True)
    customer_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Deliveries'
    
    def __str__(self):
        return f"Livraison {self.order.order_number} - {self.delivery_person.user.username}"
    
    def save(self, *args, **kwargs):
        # Calculer les gains du livreur
        if self.delivery_fee:
            commission = self.delivery_fee * (self.commission_rate / 100)
            self.earnings = self.delivery_fee - commission + self.tip_amount
        super().save(*args, **kwargs)


class DeliveryTracking(models.Model):
    """Suivi en temps réel des livraisons"""
    
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='tracking_points')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Informations supplémentaires
    speed = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # km/h
    heading = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # degrés
    accuracy = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # mètres
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Position {self.delivery.order.order_number} - {self.timestamp}"


class DeliveryRating(models.Model):
    """Évaluations des livreurs par les clients"""
    
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name='rating')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Notes (1-5 étoiles)
    overall_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuality = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    professionalism = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    food_condition = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Commentaire
    comment = models.TextField(blank=True)
    
    # Pourboire
    tip_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Évaluation {self.delivery.order.order_number} - {self.overall_rating}★"


class DeliveryZone(models.Model):
    """Zones de livraison définies"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Polygone de la zone (format GeoJSON)
    polygon_coordinates = models.JSONField()
    
    # Tarification
    base_delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    per_km_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.50)
    
    # Disponibilité
    is_active = models.BooleanField(default=True)
    peak_hours_start = models.TimeField(blank=True, null=True)
    peak_hours_end = models.TimeField(blank=True, null=True)
    peak_hours_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class DeliveryPersonSchedule(models.Model):
    """Horaires de travail des livreurs"""
    
    DAYS_OF_WEEK = [
        ('monday', 'Lundi'),
        ('tuesday', 'Mardi'),
        ('wednesday', 'Mercredi'),
        ('thursday', 'Jeudi'),
        ('friday', 'Vendredi'),
        ('saturday', 'Samedi'),
        ('sunday', 'Dimanche'),
    ]
    
    delivery_person = models.ForeignKey(DeliveryPersonProfile, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['delivery_person', 'day_of_week']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.delivery_person.user.username} - {self.get_day_of_week_display()}"


class DeliveryIssue(models.Model):
    """Problèmes rapportés pendant les livraisons"""
    
    ISSUE_TYPES = [
        ('address_not_found', 'Adresse introuvable'),
        ('customer_unavailable', 'Client indisponible'),
        ('wrong_order', 'Commande incorrecte'),
        ('damaged_food', 'Nourriture endommagée'),
        ('payment_issue', 'Problème de paiement'),
        ('vehicle_breakdown', 'Panne de véhicule'),
        ('weather_condition', 'Conditions météorologiques'),
        ('other', 'Autre'),
    ]
    
    ISSUE_STATUS = [
        ('reported', 'Signalé'),
        ('investigating', 'En cours d\'investigation'),
        ('resolved', 'Résolu'),
        ('escalated', 'Escaladé'),
    ]
    
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='issues')
    issue_type = models.CharField(max_length=30, choices=ISSUE_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=ISSUE_STATUS, default='reported')
    
    # Résolution
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='resolved_issues')
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    # Métadonnées
    reported_at = models.DateTimeField(auto_now_add=True)
    photo_evidence = models.ImageField(upload_to='issue_photos/', blank=True, null=True)
    
    class Meta:
        ordering = ['-reported_at']
    
    def __str__(self):
        return f"Problème {self.delivery.order.order_number} - {self.get_issue_type_display()}"


class DeliveryPayment(models.Model):
    """Paiements aux livreurs"""
    
    PAYMENT_STATUS = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('paid', 'Payé'),
        ('failed', 'Échoué'),
    ]
    
    delivery_person = models.ForeignKey(DeliveryPersonProfile, on_delete=models.CASCADE, related_name='payments')
    
    # Période de paiement
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Montants
    total_deliveries = models.PositiveIntegerField()
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    total_tips = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    bonus_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Statut
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Détails de paiement
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['delivery_person', 'period_start', 'period_end']
    
    def __str__(self):
        return f"Paiement {self.delivery_person.user.username} - {self.period_start} à {self.period_end}"
