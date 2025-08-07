from django.urls import path
from . import views

app_name = 'livreur'

urlpatterns = [
    # Dashboard livreur
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Gestion du profil livreur
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Gestion des livraisons
    path('deliveries/', views.delivery_list_view, name='delivery_list'),
    path('delivery/<int:delivery_id>/', views.delivery_detail_view, name='delivery_detail'),
    path('delivery/<int:delivery_id>/accept/', views.accept_delivery_view, name='accept_delivery'),
    path('delivery/<int:delivery_id>/pickup/', views.pickup_delivery_view, name='pickup_delivery'),
    path('delivery/<int:delivery_id>/complete/', views.complete_delivery_view, name='complete_delivery'),
    path('delivery/<int:delivery_id>/report-issue/', views.report_issue_view, name='report_issue'),
    
    # Suivi de position
    path('update-location/', views.update_location_view, name='update_location'),
    path('toggle-availability/', views.toggle_availability_view, name='toggle_availability'),
    
    # Navigation
    path('delivery/<int:delivery_id>/navigate/', views.navigate_view, name='navigate'),
    
    # Historique et statistiques
    path('history/', views.delivery_history_view, name='delivery_history'),
    path('earnings/', views.earnings_view, name='earnings'),
    path('statistics/', views.statistics_view, name='statistics'),
    
    # Horaires de travail
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/edit/', views.edit_schedule_view, name='edit_schedule'),
    
    # Support
    path('support/', views.support_view, name='support'),
    path('issues/', views.issue_list_view, name='issue_list'),
]