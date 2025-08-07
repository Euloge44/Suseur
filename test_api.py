#!/usr/bin/env python3
"""
Script de test simple pour l'API Restaurant Management
Nécessite que le serveur Django soit lancé sur http://localhost:8000
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_restaurants_api():
    """Teste les endpoints de l'API restaurants"""
    print("🧪 Test de l'API Restaurant Management")
    print("=" * 50)
    
    try:
        # Test GET /api/restaurants/
        print("📋 Test: Liste des restaurants")
        response = requests.get(f"{BASE_URL}/restaurants/")
        if response.status_code == 200:
            restaurants = response.json()
            print(f"✅ Succès: {len(restaurants.get('results', []))} restaurants trouvés")
        else:
            print(f"❌ Erreur: Status {response.status_code}")
        
        # Test GET /api/restaurants/active/
        print("\n📋 Test: Restaurants actifs seulement")
        response = requests.get(f"{BASE_URL}/restaurants/active/")
        if response.status_code == 200:
            active_restaurants = response.json()
            print(f"✅ Succès: {len(active_restaurants)} restaurants actifs")
        else:
            print(f"❌ Erreur: Status {response.status_code}")
        
        # Test POST /api/restaurants/
        print("\n➕ Test: Création d'un nouveau restaurant")
        new_restaurant = {
            "name": "Test Restaurant",
            "address": "123 Test Street",
            "phone": "01 23 45 67 89",
            "email": "test@restaurant.com",
            "description": "Restaurant de test",
            "capacity": 30,
            "opening_time": "12:00:00",
            "closing_time": "22:00:00",
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/restaurants/", json=new_restaurant)
        if response.status_code == 201:
            created = response.json()
            print(f"✅ Succès: Restaurant créé avec l'ID {created['id']}")
            
            # Test GET d'un restaurant spécifique
            print(f"\n📄 Test: Récupération du restaurant {created['id']}")
            response = requests.get(f"{BASE_URL}/restaurants/{created['id']}/")
            if response.status_code == 200:
                print("✅ Succès: Restaurant récupéré")
            else:
                print(f"❌ Erreur: Status {response.status_code}")
        else:
            print(f"❌ Erreur: Status {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("Assurez-vous que le serveur Django est lancé avec:")
        print("python manage.py runserver")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    test_restaurants_api()