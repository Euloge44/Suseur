# Restaurant Management System

Un système de gestion de restaurant développé avec Django et Django REST Framework.

## Installation

1. **Cloner le projet** (si ce n'est pas déjà fait)
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
   
   Si vous obtenez une erreur "externally-managed-environment", créez d'abord un environnement virtuel :
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur Linux/Mac
   # ou
   venv\Scripts\activate  # Sur Windows
   pip install -r requirements.txt
   ```

3. **Effectuer les migrations** :
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Créer un superutilisateur** (optionnel) :
   ```bash
   python manage.py createsuperuser
   ```

5. **Charger les données d'exemple** (optionnel) :
   ```bash
   python manage.py loaddata api/fixtures/restaurants.json
   ```

6. **Lancer le serveur** :
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Restaurants

- `GET /api/restaurants/` - Liste tous les restaurants
- `POST /api/restaurants/` - Crée un nouveau restaurant
- `GET /api/restaurants/{id}/` - Récupère un restaurant spécifique
- `PUT /api/restaurants/{id}/` - Met à jour un restaurant
- `DELETE /api/restaurants/{id}/` - Supprime un restaurant
- `GET /api/restaurants/active/` - Liste uniquement les restaurants actifs
- `POST /api/restaurants/{id}/activate/` - Active un restaurant
- `POST /api/restaurants/{id}/deactivate/` - Désactive un restaurant

### Filtres

- `?is_active=true` - Filtre par statut actif
- `?is_active=false` - Filtre par statut inactif

## Modèle Restaurant

Le modèle Restaurant contient les champs suivants :

- `name` : Nom du restaurant
- `address` : Adresse complète
- `phone` : Numéro de téléphone
- `email` : Adresse email
- `description` : Description du restaurant
- `capacity` : Capacité d'accueil
- `opening_time` : Heure d'ouverture
- `closing_time` : Heure de fermeture
- `is_active` : Statut actif/inactif
- `created_at` : Date de création
- `updated_at` : Date de dernière modification

## Administration

Accédez à l'interface d'administration Django à l'adresse `http://localhost:8000/admin/` après avoir créé un superutilisateur.

## Structure du projet

```
restaurant_management/
├── manage.py
├── requirements.txt
├── restaurant_management/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── api/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── urls.py
    └── views.py
```