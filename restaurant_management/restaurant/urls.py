from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # Dashboard restaurant
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Gestion du profil restaurant
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Gestion des menus
    path('menu/', views.menu_view, name='menu'),
    path('menu/add-category/', views.add_category_view, name='add_category'),
    path('menu/category/<int:category_id>/edit/', views.edit_category_view, name='edit_category'),
    path('menu/category/<int:category_id>/delete/', views.delete_category_view, name='delete_category'),
    
    # Gestion des plats
    path('menu/add-item/', views.add_menu_item_view, name='add_menu_item'),
    path('menu/item/<int:item_id>/edit/', views.edit_menu_item_view, name='edit_menu_item'),
    path('menu/item/<int:item_id>/delete/', views.delete_menu_item_view, name='delete_menu_item'),
    
    # Gestion des commandes
    path('orders/', views.order_list_view, name='order_list'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('order/<int:order_id>/update-status/', views.update_order_status_view, name='update_order_status'),
    
    # Gestion des stocks
    path('stocks/', views.stock_list_view, name='stock_list'),
    path('stocks/add/', views.add_stock_view, name='add_stock'),
    path('stock/<int:stock_id>/edit/', views.edit_stock_view, name='edit_stock'),
    path('stock/<int:stock_id>/delete/', views.delete_stock_view, name='delete_stock'),
    
    # Statistiques et rapports
    path('analytics/', views.analytics_view, name='analytics'),
    path('reviews/', views.reviews_view, name='reviews'),
    
    # Promotions
    path('promotions/', views.promotion_list_view, name='promotion_list'),
    path('promotions/add/', views.add_promotion_view, name='add_promotion'),
    path('promotion/<int:promotion_id>/edit/', views.edit_promotion_view, name='edit_promotion'),
    path('promotion/<int:promotion_id>/delete/', views.delete_promotion_view, name='delete_promotion'),
    
    # Gestion des livreurs
    path('delivery-partners/', views.delivery_partners_view, name='delivery_partners'),
]