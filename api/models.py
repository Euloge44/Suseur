from django.db import models


class Restaurant(models.Model):
    """Modèle représentant un restaurant"""
    name = models.CharField(max_length=200, verbose_name="Nom")
    address = models.TextField(verbose_name="Adresse")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    description = models.TextField(blank=True, verbose_name="Description")
    capacity = models.PositiveIntegerField(verbose_name="Capacité")
    opening_time = models.TimeField(verbose_name="Heure d'ouverture")
    closing_time = models.TimeField(verbose_name="Heure de fermeture")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"
        ordering = ['name']

    def __str__(self):
        return self.name