from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('role-selection/', views.role_selection_view, name='role_selection'),
    
    # Profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Administration
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]