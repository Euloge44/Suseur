#!/bin/bash

echo "🏗️  Configuration du projet Restaurant Management System"
echo "=================================================="

# Créer un environnement virtuel si il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📚 Installation des dépendances..."
pip install -r requirements.txt

# Effectuer les migrations
echo "🗄️  Création des migrations..."
python manage.py makemigrations

echo "🗄️  Application des migrations..."
python manage.py migrate

echo "📊 Chargement des données d'exemple..."
python manage.py loaddata api/fixtures/restaurants.json

echo "✅ Configuration terminée !"
echo ""
echo "Pour lancer le serveur :"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Pour créer un superutilisateur :"
echo "  source venv/bin/activate"
echo "  python manage.py createsuperuser"