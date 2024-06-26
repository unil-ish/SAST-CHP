"""
Extraire les informations sur des lieux de Google Maps

Extrait les informations relatives aux lieux contenus dans le
dict places. Utilise l'API Serp pour interroger et récupérer
le nom, l'id Google Maps, la description textuelle, le(s) type(s),
la latitude, la longitude, la note, le nombre d'avis, et l'adresse

Le code iso du pays où est situé le lieu est également récupéré à
l'aide de l'API GeoNames.

Le titre et l'url de la page wikipédia en anglais du lieu est ajoutée
grâce à l'API Wikimedia.

Les résultats sont écrits dans outputs/places.json

**NB** serpapi nécessite python 3.7 !!
"""

# Nécessite python 3.7(.16)
import json
import requests
from serpapi import GoogleSearch

# Définir quelques lieux
places = {
    "Tour Eiffel": "Tour Eiffel",
    "Colisee": "Colosseum",
    "Acropole": "Acropolis",
    "Masjid al-Haram": "Masjid al-Haram",
    "Fontaine de Trevi": "Trevi fountain",
    "Porte de l'Inde": "Gateway Of India",
    "Place de la Constitution": "Plaza de la Constitución, Mexico",
    "Musée du Louvre": "Louvre Museum",
    "Taj Mahal": "Taj Mahal"
}

# Définir les paramètres de recherche des lieux
gmaps_place_params = {
  "engine": "google_maps",
  "type": "search",
  "google_domain": "google.com",
  "hl": "en",
  "api_key": "cle_api" # cle api
}

# Initialiser les lieux
places_info = {}



# Fonction pour récupérer le code iso du pays sur GeoNames
def get_country_iso(lat, lng):
    """
    Récupère le code ISO d'un pays à l'aide de coordonnées
    latitude et longitude (WGS84)

    Parameters:
    lat (float): La latitude du point
    lng (float): La longitude du point

    Returns:
    string: Le code ISO 3166-1 alpha-2 du pays où est situé le point
    """

    # URL de l'API de GeoNames pour les codes de pays
    base_url = "http://api.geonames.org/countryCode"
    # Paramètres (remplir le username)
    params = {
        "lat": lat,
        "lng": lng,
        "type": "JSON",
        "username": "" # nom_utilisateur
    }
    # Réponse retournée
    response = requests.get(base_url, params=params, timeout=5000)
    # Extraire le json
    data = response.json()
    # Retourner le code du pays
    return data.get("countryCode")

def search_wikipedia(nom_lieu):
    """
    Récupère le titre et l'URL de la première page wikipédia
    (en anglais) correspondant au nom du lieu'

    Parameters:
    nom_lieu (string): Nom du lieu

    Returns:
    dict: Un dict contenant le titre (title) et l'url de la page Wikipédia

    Code adapté de https://api.wikimedia.org/wiki/Searching_for_Wikipedia_articles_using_Python
    """
    # Remplacer ici le jeton API Wikimédia
    headers = {
    'Authorization': 'Bearer API_ACCESS_TOKEN'
    }
    # Définir l'url en fonction de la langue (ici 'en')
    base_url = 'https://api.wikimedia.org/core/v1/wikipedia/'
    endpoint = '/search/page'
    url = base_url + 'en' + endpoint

    # Limiter les résultats à la première page correspondante
    parameters = {'q': nom_lieu, 'limit': 1}

    # Réponse retournée et extraire le json
    response = requests.get(url, headers=headers, params=parameters, timeout=5000)
    response_data = json.loads(response.text)
    # Premier (et seul) résultat
    page = response_data['pages'][0]
    # Ajouter au dict de résultat
    result_wiki = {
        'title': page['title'],
        'url': f"https://en.wikipedia.org/wiki/{page['key']}"
    }
    # Retourner le résultat
    return result_wiki

# Itérer sur les lieux
for nom, name in places.items():
    # Ajouter l'id du lieu aux paramètres
    gmaps_place_params["q"] = name
    # Lancer la recherche et extraire les résultats
    search_place = GoogleSearch(gmaps_place_params)
    rslts_place = search_place.get_dict()

    # Récupérer le premier résultat
    rslts_place = rslts_place['local_results'][0]

    # Préparer l'array de reviews
    place_info = {}
    # Récupérer les informations utiles
    place_info['name'] = rslts_place['title']
    place_info['place_id'] = rslts_place['place_id']
    place_info['description'] = rslts_place['description']
    place_info['type_ids'] = rslts_place.get('type_ids', [])
    place_info['latitude'] = round(rslts_place['gps_coordinates']['latitude'], 5)
    place_info['longitude'] = round(rslts_place['gps_coordinates']['longitude'], 5)
    place_info['rating'] = rslts_place['rating']
    place_info['num_reviews'] = rslts_place['reviews']
    place_info['adresse']= rslts_place['address']

    # Récupérer le code du pays
    place_info['country_iso'] = get_country_iso(place_info['latitude'], place_info['longitude'])

    # Récupérer la page wikipédia
    rslts_wikipedia = search_wikipedia(name)
    place_info['wiki_title'] = rslts_wikipedia['title']
    place_info['wiki_url']= rslts_wikipedia['url']

    # Ajouter au résultat final
    places_info[nom] = place_info

# Exporter les résultats
with open("outputs/places.json", "w", encoding="utf-8") as outfile:
    json.dump(places_info, outfile)
