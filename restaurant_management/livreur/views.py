from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from .models import DeliveryPersonProfile, Delivery, DeliveryTracking, DeliveryRating, DeliveryPersonSchedule
from client.models import Order
from core.models import User


@login_required
def dashboard_view(request):
    """Dashboard principal du livreur"""
    if request.user.role != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        delivery_profile = request.user.delivery_profile
    except DeliveryPersonProfile.DoesNotExist:
        messages.error(request, 'Profil livreur non trouvé.')
        return redirect('home')
    
    # Statistiques du livreur
    total_deliveries = delivery_profile.total_deliveries
    successful_deliveries = delivery_profile.successful_deliveries
    success_rate = delivery_profile.success_rate
    average_rating = delivery_profile.average_rating
    total_earnings = delivery_profile.total_earnings
    
    # Livraisons en cours
    active_deliveries = Delivery.objects.filter(
        delivery_person=delivery_profile,
        status__in=['assigned', 'accepted', 'picked_up', 'in_transit']
    )
    
    # Livraisons disponibles
    available_deliveries = Delivery.objects.filter(
        status='assigned',
        delivery_person__isnull=True
    )[:5]
    
    # Gains de la semaine
    from datetime import timedelta
    week_start = timezone.now() - timedelta(days=7)
    week_earnings = Delivery.objects.filter(
        delivery_person=delivery_profile,
        status='delivered',
        delivered_at__gte=week_start
    ).aggregate(total=Sum('earnings'))['total'] or 0
    
    context = {
        'delivery_profile': delivery_profile,
        'total_deliveries': total_deliveries,
        'successful_deliveries': successful_deliveries,
        'success_rate': success_rate,
        'average_rating': average_rating,
        'total_earnings': total_earnings,
        'week_earnings': week_earnings,
        'active_deliveries': active_deliveries,
        'available_deliveries': available_deliveries,
    }
    
    return render(request, 'livreur/dashboard.html', context)


@login_required
def profile_view(request):
    """Profil du livreur"""
    if request.user.role != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        delivery_profile = request.user.delivery_profile
    except DeliveryPersonProfile.DoesNotExist:
        messages.error(request, 'Profil livreur non trouvé.')
        return redirect('home')
    
    context = {
        'delivery_profile': delivery_profile,
    }
    
    return render(request, 'livreur/profile.html', context)


@login_required
def delivery_list_view(request):
    """Liste des livraisons du livreur"""
    if request.user.role != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        delivery_profile = request.user.delivery_profile
    except DeliveryPersonProfile.DoesNotExist:
        messages.error(request, 'Profil livreur non trouvé.')
        return redirect('home')
    
    # Filtres
    status_filter = request.GET.get('status', '')
    deliveries = Delivery.objects.filter(delivery_person=delivery_profile)
    
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    deliveries = deliveries.order_by('-assigned_at')
    
    # Statuts pour le filtre
    delivery_statuses = Delivery.DELIVERY_STATUS
    
    context = {
        'delivery_profile': delivery_profile,
        'deliveries': deliveries,
        'delivery_statuses': delivery_statuses,
        'status_filter': status_filter,
    }
    
    return render(request, 'livreur/delivery_list.html', context)


@login_required
def delivery_detail_view(request, delivery_id):
    """Détails d'une livraison"""
    if request.user.role != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        delivery_profile = request.user.delivery_profile
        delivery = get_object_or_404(Delivery, id=delivery_id, delivery_person=delivery_profile)
    except DeliveryPersonProfile.DoesNotExist:
        messages.error(request, 'Profil livreur non trouvé.')
        return redirect('home')
    
    context = {
        'delivery_profile': delivery_profile,
        'delivery': delivery,
    }
    
    return render(request, 'livreur/delivery_detail.html', context)


@login_required
@require_POST
def accept_delivery_view(request, delivery_id):
    """Accepter une livraison"""
    if request.user.role != 'livreur':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        delivery_profile = request.user.delivery_profile
        delivery = get_object_or_404(Delivery, id=delivery_id, status='assigned')
        
        # Vérifier que le livreur est disponible
        if delivery_profile.status != 'available':
            return JsonResponse({'error': 'Vous n\'êtes pas disponible'}, status=400)
        
        # Accepter la livraison
        delivery.delivery_person = delivery_profile
        delivery.status = 'accepted'
        delivery.accepted_at = timezone.now()
        delivery.save()
        
        # Mettre à jour le statut du livreur
        delivery_profile.status = 'busy'
        delivery_profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Livraison acceptée avec succès'
        })
        
    except DeliveryPersonProfile.DoesNotExist:
        return JsonResponse({'error': 'Profil livreur non trouvé'}, status=404)


@login_required
@require_POST
def pickup_delivery_view(request, delivery_id):
    """Confirmer la récupération de la commande"""
    if request.user.role != 'livreur':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        delivery_profile = request.user.delivery_profile
        delivery = get_object_or_404(Delivery, id=delivery_id, delivery_person=delivery_profile)
        
        if delivery.status != 'accepted':
            return JsonResponse({'error': 'Statut de livraison invalide'}, status=400)
        
        delivery.status = 'picked_up'
        delivery.picked_up_at = timezone.now()
        delivery.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Commande récupérée avec succès'
        })
        
    except DeliveryPersonProfile.DoesNotExist:
        return JsonResponse({'error': 'Profil livreur non trouvé'}, status=404)


@login_required
@require_POST
def complete_delivery_view(request, delivery_id):
    """Confirmer la livraison terminée"""
    if request.user.role != 'livreur':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        delivery_profile = request.user.delivery_profile
        delivery = get_object_or_404(Delivery, id=delivery_id, delivery_person=delivery_profile)
        
        if delivery.status not in ['picked_up', 'in_transit']:
            return JsonResponse({'error': 'Statut de livraison invalide'}, status=400)
        
        delivery.status = 'delivered'
        delivery.delivered_at = timezone.now()
        delivery.save()
        
        # Mettre à jour les statistiques du livreur
        delivery_profile.total_deliveries += 1
        delivery_profile.successful_deliveries += 1
        delivery_profile.total_earnings += delivery.earnings
        delivery_profile.status = 'available'  # Redevenir disponible
        delivery_profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Livraison terminée avec succès'
        })
        
    except DeliveryPersonProfile.DoesNotExist:
        return JsonResponse({'error': 'Profil livreur non trouvé'}, status=404)


@login_required
@require_POST
def update_location_view(request):
    """Mettre à jour la position du livreur"""
    if request.user.role != 'livreur':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        delivery_profile = request.user.delivery_profile
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if latitude and longitude:
            delivery_profile.current_latitude = latitude
            delivery_profile.current_longitude = longitude
            delivery_profile.last_location_update = timezone.now()
            delivery_profile.save()
            
            # Enregistrer le suivi pour les livraisons actives
            active_delivery = Delivery.objects.filter(
                delivery_person=delivery_profile,
                status__in=['picked_up', 'in_transit']
            ).first()
            
            if active_delivery:
                DeliveryTracking.objects.create(
                    delivery=active_delivery,
                    latitude=latitude,
                    longitude=longitude
                )
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'error': 'Coordonnées manquantes'}, status=400)
        
    except DeliveryPersonProfile.DoesNotExist:
        return JsonResponse({'error': 'Profil livreur non trouvé'}, status=404)


@login_required
@require_POST
def toggle_availability_view(request):
    """Changer le statut de disponibilité"""
    if request.user.role != 'livreur':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        delivery_profile = request.user.delivery_profile
        
        if delivery_profile.status == 'available':
            delivery_profile.status = 'offline'
            message = 'Vous êtes maintenant hors ligne'
        elif delivery_profile.status == 'offline':
            delivery_profile.status = 'available'
            message = 'Vous êtes maintenant disponible'
        else:
            return JsonResponse({'error': 'Impossible de changer le statut'}, status=400)
        
        delivery_profile.save()
        
        return JsonResponse({
            'success': True,
            'status': delivery_profile.status,
            'message': message
        })
        
    except DeliveryPersonProfile.DoesNotExist:
        return JsonResponse({'error': 'Profil livreur non trouvé'}, status=404)


@login_required
def delivery_history_view(request):
    """Historique des livraisons"""
    if request.user.role != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        delivery_profile = request.user.delivery_profile
    except DeliveryPersonProfile.DoesNotExist:
        messages.error(request, 'Profil livreur non trouvé.')
        return redirect('home')
    
    deliveries = Delivery.objects.filter(
        delivery_person=delivery_profile,
        status='delivered'
    ).order_by('-delivered_at')
    
    context = {
        'delivery_profile': delivery_profile,
        'deliveries': deliveries,
    }
    
    return render(request, 'livreur/delivery_history.html', context)


@login_required
def earnings_view(request):
    """Suivi des gains"""
    if request.user.role != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        delivery_profile = request.user.delivery_profile
    except DeliveryPersonProfile.DoesNotExist:
        messages.error(request, 'Profil livreur non trouvé.')
        return redirect('home')
    
    # Gains par période
    from datetime import timedelta
    today = timezone.now().date()
    week_start = today - timedelta(days=7)
    month_start = today - timedelta(days=30)
    
    today_earnings = Delivery.objects.filter(
        delivery_person=delivery_profile,
        status='delivered',
        delivered_at__date=today
    ).aggregate(total=Sum('earnings'))['total'] or 0
    
    week_earnings = Delivery.objects.filter(
        delivery_person=delivery_profile,
        status='delivered',
        delivered_at__date__gte=week_start
    ).aggregate(total=Sum('earnings'))['total'] or 0
    
    month_earnings = Delivery.objects.filter(
        delivery_person=delivery_profile,
        status='delivered',
        delivered_at__date__gte=month_start
    ).aggregate(total=Sum('earnings'))['total'] or 0
    
    context = {
        'delivery_profile': delivery_profile,
        'today_earnings': today_earnings,
        'week_earnings': week_earnings,
        'month_earnings': month_earnings,
        'total_earnings': delivery_profile.total_earnings,
    }
    
    return render(request, 'livreur/earnings.html', context)


@login_required
def statistics_view(request):
    """Statistiques personnelles du livreur"""
    if request.user.role != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        delivery_profile = request.user.delivery_profile
    except DeliveryPersonProfile.DoesNotExist:
        messages.error(request, 'Profil livreur non trouvé.')
        return redirect('home')
    
    # Statistiques générales
    total_deliveries = delivery_profile.total_deliveries
    successful_deliveries = delivery_profile.successful_deliveries
    success_rate = delivery_profile.success_rate
    average_rating = delivery_profile.average_rating
    
    # Temps moyen de livraison
    avg_delivery_time = Delivery.objects.filter(
        delivery_person=delivery_profile,
        status='delivered'
    ).aggregate(avg_time=Avg('travel_time_minutes'))['avg_time'] or 0
    
    context = {
        'delivery_profile': delivery_profile,
        'total_deliveries': total_deliveries,
        'successful_deliveries': successful_deliveries,
        'success_rate': success_rate,
        'average_rating': average_rating,
        'avg_delivery_time': avg_delivery_time,
    }
    
    return render(request, 'livreur/statistics.html', context)


# Vues factices pour les autres fonctionnalités
@login_required
def edit_profile_view(request):
    """Modifier le profil du livreur"""
    return render(request, 'livreur/edit_profile.html')


@login_required
def report_issue_view(request, delivery_id):
    """Signaler un problème"""
    return render(request, 'livreur/report_issue.html')


@login_required
def navigate_view(request, delivery_id):
    """Navigation vers la destination"""
    return render(request, 'livreur/navigate.html')


@login_required
def schedule_view(request):
    """Horaires de travail"""
    return render(request, 'livreur/schedule.html')


@login_required
def edit_schedule_view(request):
    """Modifier les horaires"""
    return render(request, 'livreur/edit_schedule.html')


@login_required
def support_view(request):
    """Support technique"""
    return render(request, 'livreur/support.html')


@login_required
def issue_list_view(request):
    """Liste des problèmes signalés"""
    return render(request, 'livreur/issue_list.html')
