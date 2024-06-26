import numpy as np
import cv2
from scipy.spatial import Delaunay
import json
import os
import tqdm
from sklearn.linear_model import LinearRegression
import json
import sys

# Paramètres de la caméra
focal_length = 3.15  # Distance focale en mm
aperture = 2.35      # Ouverture
angle_diagonal = 16  # Angle de vue diagonal en degrés

def process_all_interactions(directory):
    for filename in os.listdir(directory):
        if filename.endswith("_user.json"):
            print(f"Traitement du fichier {filename}...")
            chemin_user = os.path.join(directory, filename)
            main(chemin_user)

def calculate_geographic_coordinates(u, v, triangles, geo_triangles, tri):
    # Verifie si le point est à l'intérieur d'un triangle avec np.cross
    for i, triangle in enumerate(triangles):
        t = triangle
        geo_t = geo_triangles[i]

        # Extrait les coordonnées des sommets du triangle
        u0 = t[0][0]
        v0 = t[0][1]
        u1 = t[1][0]
        v1 = t[1][1]
        u2 = t[2][0]
        v2 = t[2][1]

        # Extrait les coordonnées géographiques des sommets du triangle
        lat0 = geo_t[0][0]
        lon0 = geo_t[0][1]
        lat1 = geo_t[1][0]
        lon1 = geo_t[1][1]
        lat2 = geo_t[2][0]
        lon2 = geo_t[2][1]

        # Calcule les coordonnées barycentriques
        alpha = ((u-u2)*(v1-v2)+(v-v2)*(u2-u1))/((u0-u2)*(v1-v2)-(v0-v2)*(u1-u2))
        beta = ((u-u2)*(v2-v0)+(v-v2)*(u0-u2))/((u0-u2)*(v1-v2)-(v0-v2)*(u1-u2))

        # Interpole les coordonnées géographiques en utilisant les coordonnées barycentriques
        lat = alpha*lat0 + beta*lat1 + (1-alpha-beta)*lat2
        lon = alpha*lon0 + beta*lon1 + (1-alpha-beta)*lon2
        if alpha >= 0 and beta >= 0 and (1-alpha-beta) >= 0:
            return lat, lon
    return -1, -1

def load_json_data(link):
    with open(link) as f:
        data = json.load(f)
    return data

def get_image_points_and_geo_coords(link):
    with open('static/triangle.json') as f:
        camera = link.split('/')[-1].split('_')[0]
        data = json.load(f)
        data = data[camera]
        image_points = np.array(data["image_points"])
        geographic_coords = data["geographic_coords"]
    return image_points, geographic_coords

def get_triangles(image_points):
    # Effectue la triangulation de Delaunay sur les points de l'image
    tri = Delaunay(image_points)
    triangles = image_points[tri.simplices]
    return triangles, tri

def convert_image_triangles_to_geo(triangles, image_points, geographic_coords):
    geo_triangles = []
    for t in triangles:
        geo_t = []
        for p in t:
            # Trouve la coordonnée géographique correspondante pour chaque point de l'image
            geo_t.append(geographic_coords[np.where((image_points == p).all(axis=1))[0][0]])
        geo_triangles.append(geo_t)
    return geo_triangles

def update_json_data(data, triangles, geo_triangles, tri):
    new_data = []

    for item in tqdm.tqdm(data):
        car_data = item["data"]
        if car_data:
            car_coordinates = [(x["x"], x["y"], x["h"], x["w"]) for x in car_data]
            car_points = np.array(car_coordinates, dtype=np.float32)
            car_points[:, 1] = car_points[:, 1] + car_points[:, 2] / 2
            car_geo_coordinates = []
            for p in car_points:
                u = p[0]
                v = p[1] + p[3] / 2
                # Calcule les coordonnées géographiques pour chaque point de voiture
                lat, lon = calculate_geographic_coordinates(u, v, triangles, geo_triangles, tri)
                car_geo_coordinates.append((lat, lon))
            new_car_data = []
            for x, (lat, lon) in zip(car_data, car_geo_coordinates):
                new_item = {
                    "lat": lat,
                    "lon": lon
                }
                if "frame_id" in x:
                    new_item["frame_id"] = x["frame_id"]
                if "time" in x:
                    new_item["time"] = x["time"]
                # print(x)
                # print(new_item)
                # # mettre une pause pour voir les coordonnées
                # time.sleep(2)
                new_car_data.append(new_item)
            item["data"] = new_car_data
        new_data.append(item)
    return new_data

def save_updated_json_data(link, new_data):
    # Sauvegarde les données JSON mises à jour dans un nouveau fichier
    link = link.replace('.json', '_geo.json')
    with open(link, 'w') as f:
        json.dump(new_data, f, indent=4)

def create_map(geo_triangles, car_geo_coordinates):
    plan = cv2.imread('static/plan.png')
    zone_map(plan)
    # triangle_map(plan, geo_triangles)
    car_geo_coordinates = [x for x in car_geo_coordinates if x["lat"] != -1 and x["lon"] != -1]
    cv2.polylines(plan, [np.array([(x["lat"], x["lon"]) for x in car_geo_coordinates]).astype(int)], False, (255, 0, 0), 2)
    cv2.imshow('plan', plan)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def triangle_map(plan, geo_triangles):
    for t in geo_triangles:
        t = np.array(t).astype(int)
        cv2.polylines(plan, [t], True, (0, 255, 0), 2)

def zone_map(plan):
    # ouverture du json qui contient les coordonnées des zones
    with open('static/ortho.json') as f:
        data = json.load(f)
        for zone, points in data.items():
            color = tuple(np.random.randint(0, 256, 3).tolist())
            # verifie si int et ext existe
            if 'int' in points and 'ext' in points:
                points_exterieur = [np.array(points["ext"]).astype(int)]
                points_interieur = [np.array(points["int"]).astype(int)]
                cv2.polylines(plan, points_exterieur, True, color, 2)
                cv2.polylines(plan, points_interieur, True, color, 2)
            else:
                points = [np.array(points).astype(int)]
                cv2.polylines(plan, points, True, color, 2)


def process_video_with_triangles(triangles, video_path, data):
    # Traite la vidéo et affiche les triangles sur chaque image

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erreur lors de l'ouverture du fichier vidéo")
        exit()
    
    ret, frame = cap.read()
    h, w = frame.shape[:2]

    # Calcul de la distance focale en pixels
    focal_length_px = (w / 2) / np.tan(np.deg2rad(angle_diagonal / 2))

    # Matrice de caméra (intrinsics)
    camera_matrix = np.array([[focal_length_px, 0, w / 2],
                            [0, focal_length_px, h / 2],
                            [0, 0, 1]])

    # Coefficients de distorsion
    dist_coeffs = np.array([-5.5, -44.22, 0, 0, -100])  # k1, k2, p1, p2, k3
    undistorted_frame = frame
    undistorted_frame = cv2.undistort(frame, camera_matrix, dist_coeffs)
    if not ret:
        print("Erreur lors de la lecture de l'image vidéo")
        exit()

    for t in triangles:
        t = t.astype(int)
        cv2.polylines(undistorted_frame, [t], True, (0, 255, 0), 2)
        # Écrit les coordonnées sur l'image
        for p in t:
            cv2.putText(undistorted_frame, f"({p[0]}, {p[1]})", (p[0], p[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # afficher le traget de data
    for x in data:
        cv2.circle(undistorted_frame, (int(x["x"]), int(x["y"])+int(x["h"])//2), 5, (255, 0, 0), -1)

    cv2.imshow('Video avec les triangles', undistorted_frame)

def smooth_trajectory(car_geo_coordinates, segment_size=15):
    """
    Lisse la trajectoire en utilisant une régression linéaire sur des segments de taille segment_size.
    """
    smoothed_coordinates = []

    for i in range(0, len(car_geo_coordinates), segment_size):
        segment = car_geo_coordinates[i:i + segment_size]
        if len(segment) < 2:
            smoothed_coordinates.extend(segment)
            continue

        lats = np.array([coord["lat"] for coord in segment]).reshape(-1, 1)
        lons = np.array([coord["lon"] for coord in segment])

        if -1 in lats or -1 in lons:
            smoothed_coordinates.extend(segment)
            continue

        model = LinearRegression().fit(lats, lons)
        lons_smoothed = model.predict(lats)
        
        for i, coord in enumerate(segment):
            smoothed_coordinates.append({"lat": coord["lat"], "lon": lons_smoothed[i], "time": coord["time"], "frame_id": coord["frame_id"]})

    return smoothed_coordinates
def main(video_name):
    print(f"Traitement de la vidéo '{video_name}'")
    # video_path = f'static/video/{video_name}.mp4'
    # json_path = f'static/video/json/{video_name}_user.json'
    json_path = video_name


    if not os.path.exists(json_path):
        print(f"Le fichier JSON '{json_path}' n'existe pas")
        exit()

    data = load_json_data(json_path)
    # met que 10 % de data
    # data = data[:int(len(data) * 0.1)]
    image_points, geographic_coords = get_image_points_and_geo_coords(json_path)
    triangles, tri = get_triangles(image_points)
    print("Debut du convertion des données en coordonnées géographiques")
    geo_triangles = convert_image_triangles_to_geo(triangles, image_points, geographic_coords)
    # id_person = data.index([x for x in data if x["Usager"] == "person"][-1])
    # process_video_with_triangles(triangles, video_path, data[id_person]["data"])
    new_data = update_json_data(data, triangles, geo_triangles, tri)
    print("Debut du traitement du lissage des données")
    for item in tqdm.tqdm(new_data):
        if item["data"]:
            car_geo_coordinates = item["data"]
            item["data"] = smooth_trajectory(car_geo_coordinates)
    # create_map(geo_triangles, new_data[id_person]["data"])
    # print(new_data[id_person]["Usager"])
    save_updated_json_data(json_path, new_data)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_name = sys.argv[1]
        main(video_name)
    else:
        video_files = "static/video/json/"
        process_all_interactions(video_files)
# commande pour lancé le script : python3 static/processing/format.py C7_Carnot_2024_02_13_08_48_54
