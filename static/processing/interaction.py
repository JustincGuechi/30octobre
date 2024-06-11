import json
import numpy as np
from shapely.geometry import Point, Polygon
import tqdm

def found_interaction(list_user, list_zone, authorised_zone):
    interactions = []
    print("Recherche des interactions de position...")
    for user in tqdm.tqdm(list_user):
        for zone, area in list_zone:
            if len(area[0]) == 2:
                # Récupérer les coordonnées du contour extérieur et intérieur
                polygon_ext_coords = area[0]['ext']
                polygon_int_coords = area[0]['int']
                
                # Créer les objets Polygon
                polygon_ext = Polygon(polygon_ext_coords)
                polygon_int = Polygon(polygon_int_coords)

                interaction_started = False
                start_time = None
                end_time = None

                for data in user["data"]:
                    if data["lat"] != -1 and data["lon"] != -1:
                        try:
                            point = Point(data["lat"], data["lon"])
                            if polygon_ext.contains(point) and not polygon_int.contains(point):
                                auth_polygon = Polygon(auth_area[0])
                                if not auth_polygon.contains(point):
                                    if not interaction_started:
                                        start_time = user["Time_code_debut"]
                                        interaction_started = True
                                    end_time = user["Time_code_fin"]
                                else:
                                    if interaction_started:
                                        interactions.append({
                                            "user": user['Usager'],
                                            "id": user['ID'],
                                            "zone": zone,
                                            "start_time": start_time,
                                            "end_time": end_time
                                        })
                                        interaction_started = False
                        except ValueError as e:
                            print(f"Invalid polygon or point coordinates 1 {zone}: {e}")

                if interaction_started:
                    interactions.append({
                        "user": user['Usager'],
                        "id": user['ID'],
                        "zone": zone,
                        "start_time": start_time,
                        "end_time": end_time
                    })

            else:
                polygon = Polygon(area[0])

                interaction_started = False
                start_time = None
                end_time = None

                for data in user["data"]:
                    if data["lat"] != -1 and data["lon"] != -1:
                        try:
                            point = Point(data["lat"], data["lon"])
                            if polygon.contains(point):
                                for auth_zone, auth_area in authorised_zone:
                                    auth_polygon = Polygon(auth_area[0])
                                    if not auth_polygon.contains(point):
                                        if not interaction_started:
                                            start_time = user["Time_code_debut"]
                                            interaction_started = True
                                        end_time = user["Time_code_fin"]
                                    else:
                                        if interaction_started:
                                            interactions.append({
                                                "user": user['Usager'],
                                                "id": user['ID'],
                                                "zone": zone,
                                                "start_time": start_time,
                                                "end_time": end_time
                                            })
                                            interaction_started = False
                        except ValueError as e:
                            print(f"Invalid polygon or point coordinates 2 {zone}: {e}")

                if interaction_started:
                    interactions.append({
                        "user": user['Usager'],
                        "id": user['ID'],
                        "zone": zone,
                        "start_time": start_time,
                        "end_time": end_time
                    })
    # return the list of interactions but only distinct ones
    return list({v['id']: v for v in interactions}.values())
# Chemin du fichier JSON
chemin_user = 'static/video/json/C7_Carnot_2024_02_13_08_48_54_user_geo.json'

# Ouvrir le fichier JSON
with open(chemin_user) as fichier:
    user = json.load(fichier)

chemin_zone = 'static/ortho.json'
# Charger les zones
with open(chemin_zone) as fichier:
    zone = json.load(fichier)

personn = ["road", "cycle_path", "bus"]
car = motocycle = ["cycle_path", "bus", "sidewalk"]
bicyle = ["bus", "sidewalk"]
bus = ["cycle_path", "sidewalk"]

# json dans user
# [
#     {
#         "ID": 1,
#         "Usager": "car",
#         "Datetime": 0.0,
#         "Time_code_debut": 0.0,
#         "Time_code_fin": 5.476190476190476,
#         "data": [
#             {
#                 "lat": 299.5997875880148,
#                 "lon": 615.4821005778682
#             },
#             {
#                 "lat": 298.8952351469737,
#                 "lon": 616.8021606158525
#             },
#             {
#                 "lat": 298.2198918166759,
#                 "lon": 618.0674940251414
#             }
#         ]
#     }
# ]

zone_banned_personn = []
zone_banned_car = []
zone_banned_motocycle = []
zone_banned_bicyle = []
zone_banned_bus = []
# personne
list_personn = [x for x in user if x["Usager"] == "person"]
for loc in personn:
    # recupere les zones qui sont interdites ou la clé de zone ressemble à loc
    zone_banned_personn.extend([zone for zone in zone if zone.startswith(loc)])
# print(zone_banned_personn)
# recuperer les polygone de zone en fonction de la liste des zones interdites
poly_banned_personn = [(z, [zone[z]]) for z in zone_banned_personn]
poly_authorised_personn = [(z, [zone[z]]) for z in zone if z not in zone_banned_personn]
interactions = found_interaction(list_personn, poly_banned_personn, poly_authorised_personn)

# voiture
list_car = [x for x in user if x["Usager"] == "car"]
for loc in car:
    # recupere les zones qui sont interdites ou la clé de zone ressemble à loc
    zone_banned_car.extend([zone for zone in zone if zone.startswith(loc)])
# recuperer les polygone de zone en fonction de la liste des zones interdites
poly_banned_car = [(z, [zone[z]]) for z in zone_banned_car]
poly_authorised_car = [(z, [zone[z]]) for z in zone if z not in zone_banned_car]
interactions.extend(found_interaction(list_car, poly_banned_car, poly_authorised_car))

# motocycle
list_motocycle = [x for x in user if x["Usager"] == "motocycle"]
for loc in motocycle:
    # recupere les zones qui sont interdites ou la clé de zone ressemble à loc
    zone_banned_motocycle.extend([zone for zone in zone if zone.startswith(loc)])
# recuperer les polygone de zone en fonction de la liste des zones interdites
poly_banned_motocycle = [(z, [zone[z]]) for z in zone_banned_motocycle]
poly_authorised_motocycle = [(z, [zone[z]]) for z in zone if z not in zone_banned_motocycle]
interactions.extend(found_interaction(list_motocycle, poly_banned_motocycle, poly_authorised_motocycle))

# bicyle
list_bicyle = [x for x in user if x["Usager"] == "bicyle"]
for loc in bicyle:
    # recupere les zones qui sont interdites ou la clé de zone ressemble à loc
    zone_banned_bicyle.extend([zone for zone in zone if zone.startswith(loc)])
# recuperer les polygone de zone en fonction de la liste des zones interdites
poly_banned_bicyle = [(z, [zone[z]]) for z in zone_banned_bicyle]
poly_authorised_bicyle = [(z, [zone[z]]) for z in zone if z not in zone_banned_bicyle]
interactions.extend(found_interaction(list_bicyle, poly_banned_bicyle, poly_authorised_bicyle))

# bus
list_bus = [x for x in user if x["Usager"] == "bus"]
for loc in bus:
    # recupere les zones qui sont interdites ou la clé de zone ressemble à loc
    zone_banned_bus.extend([zone for zone in zone if zone.startswith(loc)])
# recuperer les polygone de zone en fonction de la liste des zones interdites
poly_banned_bus = [(z, [zone[z]]) for z in zone_banned_bus]
poly_authorised_bus = [(z, [zone[z]]) for z in zone if z not in zone_banned_bus]
interactions.extend(found_interaction(list_bus, poly_banned_bus, poly_authorised_bus))
# print(poly_banned_personn)

# trie par time_code_debut
interactions = sorted(interactions, key=lambda x: x["start_time"])
# mettre interactions dans un fichier json
link = chemin_user.split(".")[0] + "_interactions.json"
with open(link, 'w') as fichier:
    json.dump(interactions, fichier)

for interaction in interactions:
    print(f"Interaction entre {interaction['user']} (ID: {interaction['id']}) et {interaction['zone']} de {interaction['start_time']} à {interaction['end_time']}")

