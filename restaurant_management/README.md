# 🍽️ Restaurant Management System

Une application web complète de gestion de restaurants développée avec Django, offrant une solution moderne et responsive pour la gestion des commandes, livraisons et paiements.

## 🚀 Fonctionnalités

### 👥 Pour les Clients
- **Prise de commande en ligne** : Navigation intuitive des menus avec personnalisation
- **Paiement sécurisé** : Support de T-Money, Flooz, cartes bancaires et PayPal
- **Suivi en temps réel** : Carte interactive avec position du livreur
- **Recherche avancée** : Filtres par cuisine, distance, avis et promotions
- **Programme de fidélité** : Points et récompenses échangeables
- **Évaluations** : Système de notation et commentaires
- **Notifications push** : Alertes sur commandes et promotions

### 🏪 Pour les Restaurants
- **Gestion des commandes** : Mise à jour des statuts en temps réel
- **Gestion des menus** : Ajout/modification de plats et catégories
- **Suivi des stocks** : Alertes sur niveaux critiques
- **Statistiques détaillées** : Analyses des ventes et tendances
- **Gestion des promotions** : Offres spéciales et réductions
- **Interface livreurs** : Coordination avec les partenaires de livraison

### 🚚 Pour les Livreurs
- **Suivi des commandes** : Visualisation des livraisons attribuées
- **Navigation optimisée** : Itinéraires avec cartes intégrées
- **Confirmation de livraison** : Notifications automatiques
- **Historique complet** : Détails des livraisons et performances
- **Suivi des gains** : Statistiques personnelles et paiements

### 🛠️ Administration
- **Gestion des utilisateurs** : CRUD complet avec gestion des rôles
- **Configuration système** : Paramètres globaux et sécurité
- **Rapports globaux** : Statistiques sur performances et tendances
- **Journal d'audit** : Traçabilité des actions importantes

## 🏗️ Architecture

### Structure du Projet
```
restaurant_management/
├── client/                 # Application client
├── restaurant/             # Application restaurant
├── livreur/               # Application livreur
├── core/                  # Application administration
├── api/                   # API REST
├── static/                # Fichiers statiques
├── templates/             # Templates Django
├── media/                 # Fichiers uploadés
└── requirements.txt       # Dépendances
```

### Technologies Utilisées
- **Backend** : Django 5.2.5, Django REST Framework
- **Frontend** : Bootstrap 5, JavaScript ES6+, Font Awesome
- **Base de données** : SQLite (dev), PostgreSQL (prod)
- **Cache** : Redis
- **Authentification** : Django Auth avec rôles personnalisés
- **Paiements** : Stripe, intégrations mobile money
- **Géolocalisation** : API HTML5 Geolocation

## ⚙️ Installation

### Prérequis
- Python 3.11+
- Node.js (pour les outils de build frontend)
- Redis (pour le cache)

### Installation Locale

1. **Cloner le projet**
```bash
git clone <repository-url>
cd restaurant_management
```

2. **Créer l'environnement virtuel**
```bash
python -m venv restaurant_env
source restaurant_env/bin/activate  # Linux/Mac
# ou
restaurant_env\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration de la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

6. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

L'application sera accessible sur `http://localhost:8000`

## 🔐 Système d'Authentification

### Rôles Utilisateurs
- **Client** : Commande et suivi des livraisons
- **Restaurant** : Gestion du restaurant et des commandes
- **Livreur** : Gestion des livraisons
- **Admin** : Administration complète du système

### Inscription
Le formulaire d'inscription unique redirige automatiquement selon le rôle :
- Client → Dashboard client
- Restaurant → Configuration restaurant
- Livreur → Profil livreur
- Admin → Interface d'administration

## 📱 Interface Utilisateur

### Design Moderne
- Interface responsive compatible mobile/tablet/desktop
- Design Material inspiré avec animations fluides
- Thème sombre/clair automatique
- Notifications toast en temps réel

### Fonctionnalités UX
- Navigation intuitive avec breadcrumbs
- Recherche en temps réel avec debounce
- Chargement progressif des données
- États de chargement avec spinners
- Validation côté client et serveur

## 🔄 API REST

### Endpoints Principaux
```
GET /api/restaurants/          # Liste des restaurants
GET /api/menu-items/          # Articles de menu
POST /api/orders/             # Créer une commande
GET /api/deliveries/          # Livraisons
POST /api/auth/login/         # Authentification API
```

### Authentification API
- Support JWT et session Django
- Permissions granulaires par rôle
- Rate limiting et throttling

## 💳 Système de Paiement

### Méthodes Supportées
- **Mobile Money** : T-Money, Flooz
- **Cartes bancaires** : Visa, Mastercard
- **Portefeuilles** : PayPal
- **Espèces** : Paiement à la livraison

### Sécurité
- Chiffrement des données sensibles
- Conformité PCI DSS
- Tokens de paiement sécurisés

## 🗺️ Géolocalisation

### Fonctionnalités
- Localisation automatique des clients
- Calcul de distance et frais de livraison
- Suivi en temps réel des livreurs
- Zones de livraison configurables
- Navigation turn-by-turn

## 📊 Analytics et Reporting

### Métriques Suivies
- Nombre de commandes et revenus
- Temps de livraison moyens
- Satisfaction client (ratings)
- Performance des restaurants
- Efficacité des livreurs

### Tableaux de Bord
- Graphiques interactifs
- Filtres par période
- Export des données
- Alertes automatiques

## 🔧 Configuration

### Variables d'Environnement
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Maps
GOOGLE_MAPS_API_KEY=your-api-key
```

### Settings par Environnement
- `settings/development.py` : Configuration développement
- `settings/production.py` : Configuration production
- `settings/testing.py` : Configuration tests

## 🧪 Tests

### Lancer les Tests
```bash
# Tests unitaires
python manage.py test

# Tests avec coverage
pytest --cov=.

# Tests d'intégration
python manage.py test --pattern="*integration*"
```

### Types de Tests
- Tests unitaires des modèles
- Tests des vues et API
- Tests d'intégration
- Tests de performance

## 🚀 Déploiement

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "restaurant_management.wsgi:application"]
```

### Production
1. Configurer PostgreSQL
2. Configurer Redis
3. Collecter les fichiers statiques : `python manage.py collectstatic`
4. Lancer avec Gunicorn : `gunicorn restaurant_management.wsgi:application`

## 📈 Performance

### Optimisations
- Cache Redis pour les requêtes fréquentes
- Lazy loading des images
- Compression des assets
- CDN pour les fichiers statiques
- Pagination des listes longues

### Monitoring
- Logs structurés avec Django
- Métriques avec Sentry
- Monitoring temps réel
- Alertes automatiques

## 🤝 Contribution

### Guidelines
1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

### Standards de Code
- PEP 8 pour Python
- ESLint pour JavaScript
- Tests requis pour nouvelles fonctionnalités
- Documentation des API

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

### Documentation
- [Guide utilisateur](docs/user-guide.md)
- [Guide développeur](docs/developer-guide.md)
- [API Documentation](docs/api.md)

### Contact
- Email : support@restaurant-app.com
- Discord : [Serveur communauté](https://discord.gg/restaurant-app)
- Issues : [GitHub Issues](https://github.com/your-repo/issues)

---

**Développé avec ❤️ pour simplifier la gestion des restaurants**