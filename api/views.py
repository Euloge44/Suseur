from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Restaurant
from .serializers import RestaurantSerializer


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les restaurants.
    Fournit les opérations CRUD complètes (Create, Read, Update, Delete).
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        """
        Optionnellement filtre les restaurants par statut actif.
        """
        queryset = Restaurant.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Action personnalisée pour activer un restaurant"""
        restaurant = self.get_object()
        restaurant.is_active = True
        restaurant.save()
        return Response({'status': 'Restaurant activé'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Action personnalisée pour désactiver un restaurant"""
        restaurant = self.get_object()
        restaurant.is_active = False
        restaurant.save()
        return Response({'status': 'Restaurant désactivé'})

    @action(detail=False)
    def active(self, request):
        """Action pour récupérer uniquement les restaurants actifs"""
        active_restaurants = Restaurant.objects.filter(is_active=True)
        serializer = self.get_serializer(active_restaurants, many=True)
        return Response(serializer.data)