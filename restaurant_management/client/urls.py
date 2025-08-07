from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    # Dashboard client
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Restaurants et menus
    path('restaurants/', views.restaurant_list_view, name='restaurant_list'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail_view, name='restaurant_detail'),
    
    # Panier
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
    path('update-cart/', views.update_cart_view, name='update_cart'),
    path('remove-from-cart/', views.remove_from_cart_view, name='remove_from_cart'),
    
    # Commandes
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_list_view, name='order_list'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('track-order/<int:order_id>/', views.track_order_view, name='track_order'),
    
    # Favoris
    path('favorites/', views.favorites_view, name='favorites'),
    path('toggle-favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    
    # Programme de fidélité
    path('loyalty/', views.loyalty_view, name='loyalty'),
    
    # Adresses
    path('addresses/', views.address_list_view, name='address_list'),
    path('addresses/add/', views.add_address_view, name='add_address'),
    path('addresses/<int:address_id>/edit/', views.edit_address_view, name='edit_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address_view, name='delete_address'),
]