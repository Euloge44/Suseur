from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm
from .models import User, Notification


def register_view(request):
    """Vue d'inscription avec redirection selon le rôle"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Créer une notification de bienvenue
            Notification.objects.create(
                user=user,
                title="Bienvenue !",
                message=f"Votre compte {user.get_role_display()} a été créé avec succès.",
                notification_type='success'
            )
            
            # Redirection selon le rôle
            if user.role == 'client':
                messages.success(request, 'Inscription réussie ! Bienvenue sur notre plateforme.')
                return redirect('client:dashboard')
            elif user.role == 'restaurant':
                messages.success(request, 'Inscription réussie ! Configurez maintenant votre restaurant.')
                return redirect('restaurant:dashboard')
            elif user.role == 'livreur':
                messages.success(request, 'Inscription réussie ! Complétez votre profil livreur.')
                return redirect('livreur:dashboard')
            else:
                return redirect('core:admin_dashboard')
    else:
        form = RegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """Vue de connexion avec redirection selon le rôle"""
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            
            # Gérer "Se souvenir de moi"
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            # Redirection selon le rôle
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            return redirect_user_by_role(user)
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def redirect_user_by_role(user):
    """Rediriger l'utilisateur selon son rôle"""
    if user.role == 'client':
        return redirect('client:dashboard')
    elif user.role == 'restaurant':
        return redirect('restaurant:dashboard')
    elif user.role == 'livreur':
        return redirect('livreur:dashboard')
    elif user.role == 'admin':
        return redirect('core:admin_dashboard')
    else:
        return redirect('home')


def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')


def home_view(request):
    """Page d'accueil"""
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)
    
    return render(request, 'core/home.html')


@login_required
def profile_view(request):
    """Vue du profil utilisateur"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('core:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'core/profile.html', {'form': form})


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard administrateur"""
    template_name = 'core/admin_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, 'Accès non autorisé.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques globales
        context['total_users'] = User.objects.count()
        context['total_clients'] = User.objects.filter(role='client').count()
        context['total_restaurants'] = User.objects.filter(role='restaurant').count()
        context['total_livreurs'] = User.objects.filter(role='livreur').count()
        
        # Notifications récentes
        context['recent_notifications'] = Notification.objects.filter(
            user=self.request.user
        )[:5]
        
        return context


@login_required
def notifications_view(request):
    """Vue des notifications de l'utilisateur"""
    notifications = request.user.notifications.all()
    
    # Marquer les notifications comme lues
    if request.method == 'POST':
        notification_ids = request.POST.getlist('notification_ids')
        Notification.objects.filter(
            id__in=notification_ids,
            user=request.user
        ).update(is_read=True)
        messages.success(request, 'Notifications marquées comme lues.')
        return redirect('core:notifications')
    
    return render(request, 'core/notifications.html', {
        'notifications': notifications
    })


@login_required
def mark_notification_read(request, notification_id):
    """Marquer une notification comme lue"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        messages.success(request, 'Notification marquée comme lue.')
    except Notification.DoesNotExist:
        messages.error(request, 'Notification non trouvée.')
    
    return redirect('core:notifications')


def role_selection_view(request):
    """Vue de sélection de rôle (page d'aide)"""
    return render(request, 'auth/role_selection.html')


# Vues d'erreur personnalisées
def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)
