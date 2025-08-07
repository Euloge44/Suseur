from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Sum, Avg
from .models import Restaurant, Category, MenuItem, Stock, Review, Promotion
from client.models import Order
from core.models import User


@login_required
def dashboard_view(request):
    """Dashboard principal du restaurant"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    # Statistiques du restaurant
    total_orders = Order.objects.filter(restaurant=restaurant).count()
    pending_orders = Order.objects.filter(restaurant=restaurant, status='pending').count()
    today_orders = Order.objects.filter(restaurant=restaurant, created_at__date__gte='2024-01-01').count()
    
    # Revenus
    total_revenue = Order.objects.filter(
        restaurant=restaurant, 
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Commandes récentes
    recent_orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')[:10]
    
    # Articles populaires
    popular_items = MenuItem.objects.filter(restaurant=restaurant).annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    # Stocks faibles
    from django.db import models
    low_stocks = Stock.objects.filter(restaurant=restaurant).filter(
        current_quantity__lte=models.F('minimum_threshold')
    )[:5]
    
    context = {
        'restaurant': restaurant,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'today_orders': today_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'popular_items': popular_items,
        'low_stocks': low_stocks,
    }
    
    return render(request, 'restaurant/dashboard.html', context)


@login_required
def profile_view(request):
    """Profil du restaurant"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    context = {
        'restaurant': restaurant,
    }
    
    return render(request, 'restaurant/profile.html', context)


@login_required
def menu_view(request):
    """Gestion du menu du restaurant"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    categories = restaurant.categories.all().prefetch_related('items')
    
    context = {
        'restaurant': restaurant,
        'categories': categories,
    }
    
    return render(request, 'restaurant/menu.html', context)


@login_required
def order_list_view(request):
    """Liste des commandes du restaurant"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    # Filtres
    status_filter = request.GET.get('status', '')
    orders = Order.objects.filter(restaurant=restaurant)
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    orders = orders.order_by('-created_at')
    
    # Statuts pour le filtre
    order_statuses = Order.ORDER_STATUS
    
    context = {
        'restaurant': restaurant,
        'orders': orders,
        'order_statuses': order_statuses,
        'status_filter': status_filter,
    }
    
    return render(request, 'restaurant/order_list.html', context)


@login_required
def order_detail_view(request, order_id):
    """Détails d'une commande"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
        order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    context = {
        'restaurant': restaurant,
        'order': order,
    }
    
    return render(request, 'restaurant/order_detail.html', context)


@login_required
@require_POST
def update_order_status_view(request, order_id):
    """Mettre à jour le statut d'une commande"""
    if request.user.role != 'restaurant':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        restaurant = request.user.restaurant_profile
        order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
        new_status = request.POST.get('status')
        
        if new_status in [choice[0] for choice in Order.ORDER_STATUS]:
            order.status = new_status
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Statut mis à jour: {order.get_status_display()}'
            })
        else:
            return JsonResponse({'error': 'Statut invalide'}, status=400)
            
    except Restaurant.DoesNotExist:
        return JsonResponse({'error': 'Restaurant non trouvé'}, status=404)


@login_required
def stock_list_view(request):
    """Gestion des stocks"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    stocks = Stock.objects.filter(restaurant=restaurant).order_by('item_name')
    
    context = {
        'restaurant': restaurant,
        'stocks': stocks,
    }
    
    return render(request, 'restaurant/stock_list.html', context)


@login_required
def analytics_view(request):
    """Analyses et statistiques du restaurant"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    # Statistiques générales
    total_orders = Order.objects.filter(restaurant=restaurant).count()
    total_revenue = Order.objects.filter(
        restaurant=restaurant, 
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    average_order_value = Order.objects.filter(
        restaurant=restaurant,
        payment_status='paid'
    ).aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    # Articles les plus vendus
    top_items = MenuItem.objects.filter(restaurant=restaurant).annotate(
        total_sold=Count('orderitem')
    ).order_by('-total_sold')[:10]
    
    context = {
        'restaurant': restaurant,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_order_value': average_order_value,
        'top_items': top_items,
    }
    
    return render(request, 'restaurant/analytics.html', context)


@login_required
def reviews_view(request):
    """Avis et évaluations du restaurant"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    reviews = Review.objects.filter(restaurant=restaurant).order_by('-created_at')
    
    context = {
        'restaurant': restaurant,
        'reviews': reviews,
    }
    
    return render(request, 'restaurant/reviews.html', context)


@login_required
def promotion_list_view(request):
    """Liste des promotions"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        restaurant = request.user.restaurant_profile
    except Restaurant.DoesNotExist:
        messages.error(request, 'Profil restaurant non trouvé.')
        return redirect('home')
    
    promotions = Promotion.objects.filter(restaurant=restaurant).order_by('-created_at')
    
    context = {
        'restaurant': restaurant,
        'promotions': promotions,
    }
    
    return render(request, 'restaurant/promotion_list.html', context)


# Vues factices pour les autres fonctionnalités
@login_required
def edit_profile_view(request):
    """Modifier le profil du restaurant"""
    if request.user.role != 'restaurant':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    return render(request, 'restaurant/edit_profile.html')


@login_required
def add_category_view(request):
    """Ajouter une catégorie"""
    return render(request, 'restaurant/add_category.html')


@login_required
def edit_category_view(request, category_id):
    """Modifier une catégorie"""
    return render(request, 'restaurant/edit_category.html')


@login_required
def delete_category_view(request, category_id):
    """Supprimer une catégorie"""
    return redirect('restaurant:menu')


@login_required
def add_menu_item_view(request):
    """Ajouter un plat au menu"""
    return render(request, 'restaurant/add_menu_item.html')


@login_required
def edit_menu_item_view(request, item_id):
    """Modifier un plat du menu"""
    return render(request, 'restaurant/edit_menu_item.html')


@login_required
def delete_menu_item_view(request, item_id):
    """Supprimer un plat du menu"""
    return redirect('restaurant:menu')


@login_required
def add_stock_view(request):
    """Ajouter un article en stock"""
    return render(request, 'restaurant/add_stock.html')


@login_required
def edit_stock_view(request, stock_id):
    """Modifier un stock"""
    return render(request, 'restaurant/edit_stock.html')


@login_required
def delete_stock_view(request, stock_id):
    """Supprimer un stock"""
    return redirect('restaurant:stock_list')


@login_required
def add_promotion_view(request):
    """Ajouter une promotion"""
    return render(request, 'restaurant/add_promotion.html')


@login_required
def edit_promotion_view(request, promotion_id):
    """Modifier une promotion"""
    return render(request, 'restaurant/edit_promotion.html')


@login_required
def delete_promotion_view(request, promotion_id):
    """Supprimer une promotion"""
    return redirect('restaurant:promotion_list')


@login_required
def delivery_partners_view(request):
    """Gestion des partenaires de livraison"""
    return render(request, 'restaurant/delivery_partners.html')
