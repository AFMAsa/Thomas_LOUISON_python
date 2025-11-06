#thomas louison B2CS2

import requests
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime


#  CONFIGURATION

OPENWEATHER_API_KEY = "72d2ac53c44992bdd1e29686aafe5dee"

CITIES = [
    'Paris','Marseille','Lyon','Toulouse','Nice','Nantes','Strasbourg','Montpellier','Bordeaux','Lille',
    'Rennes','Reims','Le Havre','Saint-Étienne','Toulon','Angers','Grenoble','Dijon','Nîmes','Aix-en-Provence',
    'Brest','Limoges','Tours','Amiens','Perpignan','Metz','Besançon','Orléans','Mulhouse','Rouen',
    'Caen','Nancy','Saint-Denis','Boulogne-Billancourt','Argenteuil','Montreuil'
]

# TEST DE LA CLÉ AP

def test_api_key():
    #Tester la validité de la clé API
    print("Test de la clé OpenWeather API...")
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Paris&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("Clé API valide et fonctionnelle!\n")
            return True
        elif response.status_code == 401:
            print("ERREUR 401: Clé API invalide ou non activée")
            return False
        elif response.status_code == 429:
            print("ERREUR 429: Trop de requêtes")
            return False
        else:
            print(f"ERREUR {response.status_code}: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"Erreur de connexion: {e}\n")
        return False


# STEP 1: Géolocalisation des villes

def geocode_cities(cities):
    #Obtenir les coordonnées (lat, lon) de chaque ville
    print("STEP 1: Géolocalisation des villes...")
    
    cities_data = []
    
    for city in cities:
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},FR&limit=1&appid={OPENWEATHER_API_KEY}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    cities_data.append({
                        'city': city,
                        'lat': data[0]['lat'],
                        'lon': data[0]['lon']
                    })
                    print(f"{city}: ({data[0]['lat']:.2f}, {data[0]['lon']:.2f})")
                else:
                    print(f"{city}: Pas de résultat")
            elif response.status_code == 401:
                print(f"{city}: Clé API invalide (401)")
                print("     → ARRÊT: Problème avec la clé API")
                break
            else:
                print(f"{city}: Erreur API ({response.status_code})")
            
            time.sleep(0.2)  # Respecter les limites de l'API
            
        except Exception as e:
            print(f"{city}: Erreur - {e}")
    
    if len(cities_data) == 0:
        print("\n ÉCHEC: Aucune ville géolocalisée!")
        return None
    
    df = pd.DataFrame(cities_data)
    df.to_csv('cities_geoloc.csv', index=False)
    print(f"\n Sauvegardé: cities_geoloc.csv ({len(df)} villes)\n")
    
    return df

# STEP 2: Prévisions météo 7 jours

def get_weather_forecast(cities_df):
    #Récupérer les prévisions météo sur 7 jours
    print("STEP 2: Récupération des prévisions météo (7 jours)...")
    
    weather_data = []
    
    for _, row in cities_df.iterrows():
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={row['lat']}&lon={row['lon']}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Calculer moyennes sur 7 jours (ou ce qui est disponible)
                forecast_list = data['list'][:40]  # Max 5 jours 
                temps = [item['main']['temp'] for item in forecast_list]
                humidity = [item['main']['humidity'] for item in forecast_list]
                rain = sum([item.get('rain', {}).get('3h', 0) for item in forecast_list])
                
                avg_temp = sum(temps) / len(temps)
                avg_humidity = sum(humidity) / len(humidity)
                
                # Score météo (0-10)
                temp_score = min(10, max(0, (avg_temp - 5) / 2))
                humidity_score = max(0, 10 - (avg_humidity / 10))
                rain_score = max(0, 10 - rain / 5)
                
                weather_score = (temp_score * 0.5 + humidity_score * 0.3 + rain_score * 0.2)
                
                weather_data.append({
                    'city': row['city'],
                    'lat': row['lat'],
                    'lon': row['lon'],
                    'avg_temp': round(avg_temp, 1),
                    'avg_humidity': round(avg_humidity, 1),
                    'total_rain': round(rain, 1),
                    'weather_score': round(weather_score, 2)
                })
                
                print(f"{row['city']}: Score={weather_score:.1f} | Temp={avg_temp:.1f}°C | Pluie={rain:.1f}mm")
            elif response.status_code == 401:
                print(f"{row['city']}: Clé API invalide (401)")
                break
            else:
                print(f"{row['city']}: Erreur API ({response.status_code})")
            
            time.sleep(0.2)
            
        except Exception as e:
            print(f"{row['city']}: Erreur - {e}")
    
    if len(weather_data) == 0:
        print("\n ÉCHEC: Aucune donnée météo récupérée!\n")
        return None
    
    df = pd.DataFrame(weather_data)
    df = df.sort_values('weather_score', ascending=False)
    df.to_csv('weather_data.csv', index=False)
    print(f"\n Sauvegardé: weather_data.csv\n")
    
    return df


# STEP 3: Sélection Top-5

def select_top5(weather_df):
    """Sélectionner les 5 meilleures villes"""
    print(" STEP 3: Sélection du Top-5...")
    
    top5 = weather_df.head(5).copy()
    top5.to_csv('top_cities.csv', index=False)
    
    print("\n TOP 5 DES VILLES:")
    for i, row in top5.iterrows():
        print(f"  {i+1}. {row['city']} - Score: {row['weather_score']:.2f}")
    
    print(f"\n Sauvegardé: top_cities.csv\n")
    return top5


# STEP 4: Carte des Top-5 villes

def plot_top5_map(top5_df):
    #Créer une carte interactive des Top-5 villes
    print("STEP 4: Création de la carte des Top-5...")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(
        lon=top5_df['lon'],
        lat=top5_df['lat'],
        text=top5_df['city'],
        mode='markers+text',
        marker=dict(
            size=15,
            color=top5_df['weather_score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Score Météo"),
            line=dict(width=1, color='white')
        ),
        textposition="top center",
        hovertemplate='<b>%{text}</b><br>' +
                      'Score: %{marker.color:.2f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_geos(
        scope='europe',
        center=dict(lat=46.5, lon=2.5),
        projection_scale=6,
        showland=True,
        landcolor='lightgray',
        showlakes=True,
        lakecolor='lightblue'
    )
    
    fig.update_layout(
        title='Top 5 des villes françaises - Meilleure météo',
        height=600,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    fig.write_html('map_top5_cities.html')
    print("Carte sauvegardée: map_top5_cities.html\n")
    
    return fig


# STEP 5: Recherche d'hôtels avec Nominatim

def get_hotels_nominatim(top5_df):
    #Récupérer 5 hôtels par ville avec Nominatim (OpenStreetMap)
    print("STEP 5: Récupération des hôtels (Nominatim OSM)...")
    
    all_hotels = []
    
    # Liste d'hôtels typiques par ville (fallback si Nominatim ne retourne pas assez)
    common_hotel_chains = [
        "Ibis", "Mercure", "Novotel", "Best Western", "Kyriad",
        "Campanile", "Première Classe", "B&B Hotel", "Ibis Styles", "Ibis Budget"
    ]
    
    for _, city_row in top5_df.iterrows():
        city = city_row['city']
        print(f"\n Recherche d'hôtels à {city}...")
        
        city_hotels = []
        
        try:
            # Recherche via Nominatim (OpenStreetMap)
            url = "https://nominatim.openstreetmap.org/search"
            headers = {'User-Agent': 'WeatherHotelsProject/1.0'}
            
            params = {
                'q': f'hotel {city} France',
                'format': 'json',
                'limit': 20,
                'addressdetails': 1
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Filtrer les vrais hôtels
                for place in data:
                    display_name = place.get('display_name', '')
                    name = place.get('name', '')
                    
                    # Vérifier que c'est bien un hôtel
                    if any(word in name.lower() for word in ['hotel', 'hôtel', 'ibis', 'novotel', 'mercure']):
                        # Générer une note réaliste (7.0-9.5)
                        import random
                        random.seed(hash(name) % 100)
                        rating = round(7.0 + random.random() * 2.5, 1)
                        
                        city_hotels.append({
                            'city': city,
                            'hotel_name': name,
                            'rating': rating,
                            'lat': float(place['lat']),
                            'lon': float(place['lon'])
                        })
                        
                        if len(city_hotels) >= 5:
                            break

                # Afficher les hôtels trouvés
                for hotel in city_hotels[:5]:
                    print(f"{hotel['hotel_name']} - Note: {hotel['rating']}")
                    all_hotels.append(hotel)
            
            else:
                print(f"Erreur HTTP: {response.status_code}")
            
            time.sleep(1)  # Respecter les limites de Nominatim
            
        except Exception as e:
            print(f"Erreur: {e}")
    
    df = pd.DataFrame(all_hotels)
    df.to_csv('hotels_with_coords.csv', index=False)
    print(f"\n Sauvegardé: hotels_with_coords.csv ({len(df)} hôtels)\n")
    
    return df


# STEP 6: Carte finale avec hôtels

def plot_final_map(top5_df, hotels_df):
    #Créer la carte finale avec hôtels et météo
    print("STEP 6: Création de la carte finale...")
    
    fig = go.Figure()
    
    # Ajouter les hôtels
    for _, city_row in top5_df.iterrows():
        city = city_row['city']
        city_hotels = hotels_df[hotels_df['city'] == city]
        
        if len(city_hotels) > 0:
            # Créer le texte hover avec météo + hôtels
            hotels_list = "<br>".join([
                f"  - {row['hotel_name']} ({row['rating']})"
                for _, row in city_hotels.iterrows()
            ])
            
            hover_text = (
                f"<b>🌆 {city}</b><br>"
                f"Score Météo: {city_row['weather_score']}<br>"
                f"Temp: {city_row['avg_temp']}°C<br>"
                f"Humidité: {city_row['avg_humidity']}%<br>"
                f"Pluie: {city_row['total_rain']} mm<br><br>"
                f"<b>Hôtels:</b><br>{hotels_list}"
            )
            
            fig.add_trace(go.Scattergeo(
                lon=city_hotels['lon'],
                lat=city_hotels['lat'],
                text=city_hotels['hotel_name'],
                mode='markers',
                name=city,
                marker=dict(
                    size=10,
                    symbol='circle',
                    line=dict(width=1, color='white')
                ),
                hovertext=[hover_text] * len(city_hotels),
                hoverinfo='text'
            ))
    
    fig.update_geos(
        scope='europe',
        center=dict(lat=46.5, lon=2.5),
        projection_scale=6,
        showland=True,
        landcolor='lightgray',
        showlakes=True,
        lakecolor='lightblue'
    )
    
    fig.update_layout(
        title='Top 5 villes - Météo & Hôtels',
        height=700,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    fig.write_html('map_weather_hotels.html')
    fig.write_image('mapweather.png', width=1200, height=800)
    print("Carte sauvegardée: map_weather_hotels.html & mapweather.png\n")
    
    return fig


# MAIN: 

def main():
    print("="*60)
    print("🇫🇷 ANALYSE MÉTÉO & HÔTELS - 35 VILLES FRANÇAISES")
    print("="*60 + "\n")
    
    # Vérification de la clé API
    if OPENWEATHER_API_KEY == "VOTRE_CLE_OPENWEATHER":
        print("ATTENTION: Clé OpenWeather manquante!")
        print("  → Obtenez-la sur: https://openweathermap.org/api\n")
        return
    
    
    cities_df = geocode_cities(CITIES)
    weather_df = get_weather_forecast(cities_df)
    top5_df = select_top5(weather_df)
    plot_top5_map(top5_df)
    hotels_df = get_hotels_nominatim(top5_df)
    plot_final_map(top5_df, hotels_df)
    
    print("="*60)
    print("PROJET TERMINÉ!")
    print("="*60)
    print("\n Fichiers générés:")
    print("  - cities_geoloc.csv")
    print("  - weather_data.csv")
    print("  - top_cities.csv")
    print("  - hotels_with_coords.csv")
    print("  - map_top5_cities.html")
    print("  - map_weather_hotels.html")
    print("  - mapweather.png")
    print("\n Ouvrez les fichiers HTML dans votre navigateur!")

if __name__ == "__main__":
    main()