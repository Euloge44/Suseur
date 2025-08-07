from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet

# Créer le routeur et enregistrer le ViewSet
router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]