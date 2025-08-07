from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import CustomerProfile, Order, Cart, CartItem, Favorite, Address
from restaurant.models import Restaurant, MenuItem
from core.models import User


@login_required
def dashboard_view(request):
    """Dashboard principal du client"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    # Créer le profil client s'il n'existe pas
    customer_profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    
    # Statistiques du client
    recent_orders = Order.objects.filter(customer=request.user)[:5]
    total_orders = Order.objects.filter(customer=request.user).count()
    
    # Restaurants favoris
    favorite_restaurants = Restaurant.objects.filter(favorited_by__customer=request.user)[:3]
    
    # Restaurants recommandés (basé sur les commandes précédentes)
    recommended_restaurants = Restaurant.objects.filter(is_active=True, is_verified=True)[:6]
    
    context = {
        'customer_profile': customer_profile,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'favorite_restaurants': favorite_restaurants,
        'recommended_restaurants': recommended_restaurants,
        'loyalty_points': customer_profile.loyalty_points,
    }
    
    return render(request, 'client/dashboard.html', context)


@login_required
def restaurant_list_view(request):
    """Liste des restaurants avec recherche et filtres"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    restaurants = Restaurant.objects.filter(is_active=True, is_verified=True)
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        restaurants = restaurants.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(cuisine_type__icontains=search_query)
        )
    
    # Filtre par type de cuisine
    cuisine_filter = request.GET.get('cuisine', '')
    if cuisine_filter:
        restaurants = restaurants.filter(cuisine_type=cuisine_filter)
    
    # Tri
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'rating':
        restaurants = restaurants.order_by('-average_rating')
    elif sort_by == 'delivery_fee':
        restaurants = restaurants.order_by('delivery_fee')
    else:
        restaurants = restaurants.order_by('name')
    
    # Types de cuisine pour le filtre
    cuisine_types = Restaurant.CUISINE_TYPES
    
    context = {
        'restaurants': restaurants,
        'cuisine_types': cuisine_types,
        'search_query': search_query,
        'cuisine_filter': cuisine_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'client/restaurant_list.html', context)


@login_required
def restaurant_detail_view(request, restaurant_id):
    """Détails d'un restaurant avec son menu"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, is_active=True)
    categories = restaurant.categories.filter(is_active=True).prefetch_related('items')
    
    # Vérifier si le restaurant est dans les favoris
    is_favorite = Favorite.objects.filter(customer=request.user, restaurant=restaurant).exists()
    
    context = {
        'restaurant': restaurant,
        'categories': categories,
        'is_favorite': is_favorite,
    }
    
    return render(request, 'client/restaurant_detail.html', context)


@login_required
def cart_view(request):
    """Vue du panier d'achat"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.all().select_related('menu_item', 'menu_item__restaurant')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'client/cart.html', context)


@login_required
@require_POST
def add_to_cart_view(request):
    """Ajouter un article au panier"""
    if request.user.role != 'client':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    menu_item_id = request.POST.get('menu_item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        menu_item = MenuItem.objects.get(id=menu_item_id, is_available=True)
        cart, created = Cart.objects.get_or_create(customer=request.user)
        
        # Vérifier si le restaurant est le même que celui du panier
        if cart.restaurant and cart.restaurant != menu_item.restaurant:
            return JsonResponse({
                'error': 'Vous ne pouvez commander que dans un seul restaurant à la fois.'
            }, status=400)
        
        # Mettre à jour le restaurant du panier
        if not cart.restaurant:
            cart.restaurant = menu_item.restaurant
            cart.save()
        
        # Ajouter ou mettre à jour l'article
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={
                'quantity': quantity,
                'unit_price': menu_item.discounted_price,
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Article ajouté au panier',
            'cart_count': cart.total_items
        })
        
    except MenuItem.DoesNotExist:
        return JsonResponse({'error': 'Article non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def order_list_view(request):
    """Liste des commandes du client"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'client/order_list.html', context)


@login_required
def order_detail_view(request, order_id):
    """Détails d'une commande"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'client/order_detail.html', context)


@login_required
def checkout_view(request):
    """Page de commande/checkout"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    cart = get_object_or_404(Cart, customer=request.user)
    
    if not cart.items.exists():
        messages.warning(request, 'Votre panier est vide.')
        return redirect('client:cart')
    
    # Adresses du client
    addresses = Address.objects.filter(customer=request.user)
    
    context = {
        'cart': cart,
        'addresses': addresses,
    }
    
    return render(request, 'client/checkout.html', context)


@login_required
def favorites_view(request):
    """Liste des restaurants favoris"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    favorites = Favorite.objects.filter(customer=request.user).select_related('restaurant')
    
    context = {
        'favorites': favorites,
    }
    
    return render(request, 'client/favorites.html', context)


@login_required
@require_POST
def toggle_favorite_view(request):
    """Ajouter/retirer un restaurant des favoris"""
    if request.user.role != 'client':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    restaurant_id = request.POST.get('restaurant_id')
    
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
        favorite, created = Favorite.objects.get_or_create(
            customer=request.user,
            restaurant=restaurant
        )
        
        if not created:
            favorite.delete()
            is_favorite = False
            message = 'Restaurant retiré des favoris'
        else:
            is_favorite = True
            message = 'Restaurant ajouté aux favoris'
        
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
        
    except Restaurant.DoesNotExist:
        return JsonResponse({'error': 'Restaurant non trouvé'}, status=404)


@login_required
def loyalty_view(request):
    """Page du programme de fidélité"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)
    loyalty_transactions = customer_profile.loyalty_transactions.all()[:20]
    
    context = {
        'customer_profile': customer_profile,
        'loyalty_transactions': loyalty_transactions,
    }
    
    return render(request, 'client/loyalty.html', context)


@login_required
def address_list_view(request):
    """Liste des adresses du client"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    addresses = Address.objects.filter(customer=request.user)
    
    context = {
        'addresses': addresses,
    }
    
    return render(request, 'client/address_list.html', context)


@login_required
def add_address_view(request):
    """Ajouter une nouvelle adresse"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    if request.method == 'POST':
        # Logique d'ajout d'adresse
        messages.success(request, 'Adresse ajoutée avec succès.')
        return redirect('client:address_list')
    
    return render(request, 'client/add_address.html')


@login_required
def track_order_view(request, order_id):
    """Suivi en temps réel d'une commande"""
    if request.user.role != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'client/track_order.html', context)


# Vues factices pour les autres fonctionnalités
@login_required
def update_cart_view(request):
    """Mettre à jour le panier"""
    return JsonResponse({'success': True})


@login_required
def remove_from_cart_view(request):
    """Retirer un article du panier"""
    return JsonResponse({'success': True})


@login_required
def edit_address_view(request, address_id):
    """Modifier une adresse"""
    return render(request, 'client/edit_address.html')


@login_required
def delete_address_view(request, address_id):
    """Supprimer une adresse"""
    return redirect('client:address_list')
