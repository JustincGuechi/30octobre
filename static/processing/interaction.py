import json
from shapely.geometry import Point, Polygon
import tqdm
import os
import sys
import uuid


def found_interaction(list_user, list_zone, authorised_zone):
    interactions = []
    print("Recherche des interactions de position...")
    for user in tqdm.tqdm(list_user):
        if 'ID2' not in user:
            user["ID2"] = str(uuid.uuid4())

        for zone, area in list_zone:
            if len(area[0]) == 2:
                polygon_ext_coords = area[0]['ext']
                polygon_int_coords = area[0]['int']
                polygon_ext = Polygon(polygon_ext_coords)
                polygon_int = Polygon(polygon_int_coords)
            else:
                polygon_ext = Polygon(area[0])
                polygon_int = None

            interaction_started = False
            start_time = None
            end_time = None

            for data in user["data"]:
                if data["lat"] != -1 and data["lon"] != -1:
                    try:
                        point = Point(data["lat"], data["lon"])
                        inside_zone = polygon_ext.contains(point) and (not polygon_int or not polygon_int.contains(point))
                        if inside_zone:
                            for auth_zone, auth_area in authorised_zone:
                                auth_polygon = Polygon(auth_area[0])
                                if not auth_polygon.contains(point):
                                    if not interaction_started:
                                        start_time = data["time"]
                                        interaction_started = True
                                    end_time = data["time"]
                                    break
                            else:
                                if interaction_started:
                                    duration = end_time - start_time
                                    interaction_type = determine_interaction_type(duration)
                                    interactions.append({
                                        "user": user['Usager'],
                                        "id_interaction": str(user['ID']) + user['ID2'],
                                        "id": [user['ID2']],
                                        "interaction": interaction_type,
                                        "zone": zone,
                                        "start_time": start_time,
                                        "end_time": end_time,
                                        "commentaire": "",
                                        "valide": False
                                    })
                                    interaction_started = False
                                    start_time = None
                                    end_time = None
                        else:
                            if interaction_started:
                                duration = end_time - start_time
                                interaction_type = determine_interaction_type(duration)
                                interactions.append({
                                    "user": user['Usager'],
                                    "id_interaction": str(user['ID']) + user['ID2'],
                                    "id": [user['ID2']],
                                    "interaction": interaction_type,
                                    "zone": zone,
                                    "start_time": start_time,
                                    "end_time": end_time,
                                    "commentaire": "",
                                    "valide": False
                                })
                                interaction_started = False
                                start_time = None
                                end_time = None

                    except ValueError as e:
                        print(f"Invalid polygon or point coordinates 1 {zone}: {e}")

            if interaction_started:
                duration = end_time - start_time
                interaction_type = determine_interaction_type(duration)
                interactions.append({
                    "user": user['Usager'],
                    "id_interaction": str(user['ID']) + user['ID2'],
                    "id": [user['ID2']],
                    "interaction": interaction_type,
                    "zone": zone,
                    "start_time": start_time,
                    "end_time": end_time,
                    "commentaire": "",
                    "valide": False
                })
    # retire dans interactions avec interaction = "Faut positif"
    interactions = [x for x in interactions if x["interaction"] != "Faut positif"]
    return interactions

def determine_interaction_type(duration):
    if duration < 100:
        return "Faut positif"
    elif duration < 200:
        return "Franchissement de ligne cours"
    elif duration < 1000:
        return "Franchissement de ligne long"
    else:
        return "Autre"

def process_interactions(chemin_user, chemin_zone):
    # Ouvrir le fichier JSON
    with open(chemin_user) as fichier:
        user = json.load(fichier)

    # Charger les zones
    with open(chemin_zone) as fichier:
        zone = json.load(fichier)

    personn = ["road", "cycle_path", "bus", "bus_road_Carnot"]
    car = motocycle = ["cycle_path", "bus", "sidewalk"]
    bicyle = ["bus", "sidewalk"]
    bus = ["cycle_path", "sidewalk"]

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

    # trie par time_code_debut
    interactions = sorted(interactions, key=lambda x: x["start_time"])

    # mettre interactions dans un fichier json
    link = chemin_user.split(".")[0] + "_interactions.json"
    with open(link, 'w') as fichier:
        json.dump(interactions, fichier, indent=4)

def process_all_interactions(directory):
    for filename in os.listdir(directory):
        if filename.endswith("_user_geo.json"):
            print(f"Traitement du fichier {filename}...")
            chemin_user = os.path.join(directory, filename)
            chemin_zone = 'static/ortho.json'
            process_interactions(chemin_user, chemin_zone)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        chemin_user = 'static/video/json/',directory
        chemin_zone = 'static/ortho.json'
        process_interactions(chemin_user, chemin_zone)
    else:
        directory = 'static/video/json'
    process_all_interactions(directory)
