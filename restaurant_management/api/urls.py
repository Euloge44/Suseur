from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'menu-items', views.MenuItemViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'deliveries', views.DeliveryViewSet)

urlpatterns = [
    # API REST
    path('', include(router.urls)),
    
    # Authentification API
    path('auth/login/', views.api_login_view, name='api_login'),
    path('auth/logout/', views.api_logout_view, name='api_logout'),
    
    # Endpoints spéciaux
    path('search/restaurants/', views.search_restaurants_view, name='search_restaurants'),
    path('track/delivery/<int:delivery_id>/', views.track_delivery_view, name='track_delivery'),
    path('location/update/', views.update_location_view, name='update_location'),
    
    # Statistiques
    path('stats/dashboard/', views.dashboard_stats_view, name='dashboard_stats'),
]