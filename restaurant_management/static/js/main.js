// Fonctions utilitaires globales
const RestaurantApp = {
    // Configuration
    config: {
        apiUrl: '/api/',
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
    },

    // Initialisation
    init() {
        this.setupEventListeners();
        this.initializeTooltips();
        this.initializeModals();
        this.setupAjaxDefaults();
        this.loadNotifications();
        this.updateCartCount();
    },

    // Configuration des événements
    setupEventListeners() {
        // Gestion des formulaires AJAX
        document.addEventListener('submit', this.handleFormSubmit.bind(this));
        
        // Gestion des boutons d'action
        document.addEventListener('click', this.handleButtonClick.bind(this));
        
        // Mise à jour automatique des notifications
        setInterval(this.loadNotifications.bind(this), 30000); // Toutes les 30 secondes
        
        // Géolocalisation pour les livreurs
        if (navigator.geolocation && document.body.classList.contains('livreur-page')) {
            this.startLocationTracking();
        }
    },

    // Initialiser les tooltips Bootstrap
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Initialiser les modales Bootstrap
    initializeModals() {
        const modalElements = document.querySelectorAll('.modal');
        modalElements.forEach(modalEl => {
            new bootstrap.Modal(modalEl);
        });
    },

    // Configuration AJAX par défaut
    setupAjaxDefaults() {
        // Configuration des headers CSRF pour jQuery si disponible
        if (typeof $ !== 'undefined') {
            $.ajaxSetup({
                beforeSend: (xhr, settings) => {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.csrfSafeMethod(settings.type)) {
                        xhr.setRequestHeader("X-CSRFToken", this.config.csrfToken);
                    }
                }
            });
        }
    },

    // Vérifier si la méthode HTTP est sûre pour CSRF
    csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    },

    // Gestion des soumissions de formulaires
    handleFormSubmit(event) {
        const form = event.target;
        
        // Formulaires AJAX
        if (form.classList.contains('ajax-form')) {
            event.preventDefault();
            this.submitAjaxForm(form);
        }
    },

    // Gestion des clics sur les boutons
    handleButtonClick(event) {
        const button = event.target.closest('button, a');
        if (!button) return;

        // Boutons d'ajout au panier
        if (button.classList.contains('add-to-cart')) {
            event.preventDefault();
            this.addToCart(button);
        }

        // Boutons de favoris
        if (button.classList.contains('toggle-favorite')) {
            event.preventDefault();
            this.toggleFavorite(button);
        }

        // Boutons de mise à jour de statut
        if (button.classList.contains('update-status')) {
            event.preventDefault();
            this.updateOrderStatus(button);
        }

        // Boutons de géolocalisation
        if (button.classList.contains('update-location')) {
            event.preventDefault();
            this.updateLocation();
        }
    },

    // Soumettre un formulaire AJAX
    async submitAjaxForm(form) {
        const formData = new FormData(form);
        const submitButton = form.querySelector('[type="submit"]');
        
        // Désactiver le bouton et afficher le loading
        if (submitButton) {
            submitButton.disabled = true;
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<span class="loading-spinner"></span> Chargement...';
            
            // Restaurer le bouton après 5 secondes max
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }, 5000);
        }

        try {
            const response = await fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-CSRFToken': this.config.csrfToken,
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(result.message || 'Opération réussie', 'success');
                
                // Actions post-soumission
                if (result.redirect) {
                    window.location.href = result.redirect;
                } else if (form.dataset.reload === 'true') {
                    window.location.reload();
                }
            } else {
                this.showNotification(result.error || 'Une erreur est survenue', 'error');
            }
        } catch (error) {
            console.error('Erreur AJAX:', error);
            this.showNotification('Erreur de connexion', 'error');
        } finally {
            // Restaurer le bouton
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }
        }
    },

    // Ajouter un article au panier
    async addToCart(button) {
        const menuItemId = button.dataset.menuItemId;
        const quantity = button.dataset.quantity || 1;

        try {
            const response = await fetch('/client/add-to-cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.config.csrfToken,
                },
                body: `menu_item_id=${menuItemId}&quantity=${quantity}`
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(result.message, 'success');
                this.updateCartCount(result.cart_count);
            } else {
                this.showNotification(result.error, 'error');
            }
        } catch (error) {
            console.error('Erreur ajout panier:', error);
            this.showNotification('Erreur lors de l\'ajout au panier', 'error');
        }
    },

    // Basculer le statut favori d'un restaurant
    async toggleFavorite(button) {
        const restaurantId = button.dataset.restaurantId;

        try {
            const response = await fetch('/client/toggle-favorite/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.config.csrfToken,
                },
                body: `restaurant_id=${restaurantId}`
            });

            const result = await response.json();

            if (result.success) {
                // Mettre à jour l'icône
                const icon = button.querySelector('i');
                if (result.is_favorite) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    button.classList.add('text-danger');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    button.classList.remove('text-danger');
                }
                
                this.showNotification(result.message, 'success');
            } else {
                this.showNotification(result.error, 'error');
            }
        } catch (error) {
            console.error('Erreur favori:', error);
            this.showNotification('Erreur lors de la mise à jour des favoris', 'error');
        }
    },

    // Mettre à jour le statut d'une commande
    async updateOrderStatus(button) {
        const orderId = button.dataset.orderId;
        const newStatus = button.dataset.status;

        if (!confirm('Êtes-vous sûr de vouloir changer ce statut ?')) {
            return;
        }

        try {
            const response = await fetch(`/restaurant/order/${orderId}/update-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.config.csrfToken,
                },
                body: `status=${newStatus}`
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(result.message, 'success');
                // Recharger la page pour mettre à jour l'affichage
                setTimeout(() => window.location.reload(), 1000);
            } else {
                this.showNotification(result.error, 'error');
            }
        } catch (error) {
            console.error('Erreur mise à jour statut:', error);
            this.showNotification('Erreur lors de la mise à jour du statut', 'error');
        }
    },

    // Mettre à jour la géolocalisation
    async updateLocation() {
        if (!navigator.geolocation) {
            this.showNotification('Géolocalisation non supportée', 'error');
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const { latitude, longitude } = position.coords;

                try {
                    const response = await fetch('/livreur/update-location/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': this.config.csrfToken,
                        },
                        body: `latitude=${latitude}&longitude=${longitude}`
                    });

                    const result = await response.json();

                    if (result.success) {
                        console.log('Position mise à jour');
                    } else {
                        console.error('Erreur position:', result.error);
                    }
                } catch (error) {
                    console.error('Erreur mise à jour position:', error);
                }
            },
            (error) => {
                console.error('Erreur géolocalisation:', error);
            }
        );
    },

    // Démarrer le suivi de géolocalisation
    startLocationTracking() {
        // Mettre à jour la position toutes les 30 secondes
        setInterval(() => {
            this.updateLocation();
        }, 30000);

        // Première mise à jour immédiate
        this.updateLocation();
    },

    // Charger les notifications
    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications/');
            const notifications = await response.json();
            
            this.updateNotificationCount(notifications.unread_count);
        } catch (error) {
            console.error('Erreur chargement notifications:', error);
        }
    },

    // Mettre à jour le compteur de notifications
    updateNotificationCount(count) {
        const badge = document.getElementById('notification-count');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    },

    // Mettre à jour le compteur du panier
    updateCartCount(count) {
        if (count !== undefined) {
            const badge = document.getElementById('cart-count');
            if (badge) {
                badge.textContent = count;
            }
        }
    },

    // Afficher une notification toast
    showNotification(message, type = 'info') {
        // Créer l'élément toast
        const toastContainer = this.getOrCreateToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${this.getBootstrapColorClass(type)} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${this.getNotificationIcon(type)} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        // Afficher le toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: type === 'error' ? 5000 : 3000
        });
        
        toast.show();
        
        // Nettoyer après fermeture
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },

    // Obtenir ou créer le conteneur des toasts
    getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    },

    // Convertir le type de notification en classe Bootstrap
    getBootstrapColorClass(type) {
        const colorMap = {
            success: 'success',
            error: 'danger',
            warning: 'warning',
            info: 'primary'
        };
        return colorMap[type] || 'primary';
    },

    // Obtenir l'icône pour le type de notification
    getNotificationIcon(type) {
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return iconMap[type] || 'fa-info-circle';
    },

    // Formater les prix
    formatPrice(price) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'XOF'
        }).format(price);
    },

    // Formater les dates
    formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },

    // Debounce pour les recherches
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Initialiser l'application quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    RestaurantApp.init();
});

// Exposer l'objet globalement pour les autres scripts
window.RestaurantApp = RestaurantApp;