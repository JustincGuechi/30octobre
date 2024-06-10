import numpy as np
import cv2
import folium
from scipy.spatial import Delaunay
import json
import os
import time
import tqdm
from sklearn.linear_model import LinearRegression
import json
# Paramètres de la caméra
focal_length = 3.15  # Distance focale en mm
aperture = 2.35      # Ouverture
angle_diagonal = 16  # Angle de vue diagonal en degrés

link_map_leaflet = 'https://tiles.arcgis.com/tiles/5e9nT6GAayqss4ni/arcgis/rest/services/ORTHO2022_5cm/MapServer/WMTS/1.0.0/WMTSCapabilities.xml'

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
    if 'C1_Thiers' in link:
        geographic_coords = [(47.322029, 5.051598), (47.321946, 5.051641), (47.321968, 5.051779), (47.322, 5.051837), (47.322011, 5.051762), (47.322061, 5.051871), (47.322163, 5.05175), (47.322148, 5.051658), (47.322115, 5.052182), (47.321746, 5.051855), (47.322039, 5.051642), (47.321699, 5.052118), (47.321727, 5.052172), (47.322106, 5.051819), (47.322132, 5.051782)]
        image_points = np.array([(345, 571), (754, 433), (539, 328), (452, 314), (428, 340), (345, 310), (91, 346), (5, 390), (303, 284), (798, 313), (318, 449), (697, 279), (653, 275), (242, 325), (178, 335)])
    elif 'C7_Carnot' in link:
        # geographic_coords = [(47.321476, 5.051601), (47.321466, 5.051609), (47.321475, 5.05164), (47.321464, 5.051664), (47.321457, 5.051622), (47.321427, 5.051628), (47.321421, 5.051584), (47.321392, 5.051589), (47.321354, 5.051552), (47.321358, 5.05158), (47.321179, 5.051523), (47.321225, 5.051605), (47.321249, 5.051624), (47.321367, 5.051687), (47.321307, 5.051739), (47.321314, 5.051774), (47.321401, 5.051737), (47.321412, 5.051759), (47.321475, 5.05173), (47.321393, 5.051819), (47.321484, 5.051648), (47.321447, 5.052043), (47.321478, 5.051966), (47.321497, 5.051698), (47.321299, 5.051899), (47.321285, 5.052094), (47.321411, 5.05155)]
        # image_points =np.array( [(584, 596), (562, 490), (353, 466), (323, 376), (524, 428), (560, 321), (722, 350), (695, 287), (776, 266), (714, 252), (751, 187), (685, 181), (640, 197), (497, 217), (477, 188), (435, 190), (360, 230), (308, 236), (156, 317), (282, 211), (260, 500), (86, 208), (0, 248), (0, 463), (359, 177), (255, 169),(797, 443)] )
        # Points de l'image pour C7_Carnot
        # image_points = np.array([[495, 217], [667, 194], [309, 234], [248, 492], [776, 298], [690, 254], [763, 213], [115, 217], [3, 284], [0, 504], [261, 173], [361, 177], [564, 568], [142, 340], [561, 324],[ 568, 220], [327, 373], [675, 289], [767, 262], [353, 466], [519, 422], [695, 345], [758, 306], [788, 287]], dtype=np.float32)
        # # Coordonnées géographiques pour C7_Carnot
        # geographic_coords = [(47.321361, 5.051694), (47.321222, 5.051583), (47.321417, 5.051750), (47.321500, 5.051639), (47.321361, 5.051528), (47.321361, 5.051583), (47.321125, 5.051428), (47.321447, 5.052046), (47.321563, 5.051865),(47.321529, 5.051678), (47.321286, 5.052094), (47.321300, 5.051900), (47.321475, 5.051601), (47.321483, 5.051722), (47.321429, 5.051628),(47.321346, 5.051657), (47.321464, 5.051666),(47.321390, 5.051593),(47.321318, 5.051514),(47.321476, 5.051640), (47.321457, 5.051622), (47.321421, 5.051584), (47.321384, 5.051546), (47.321348, 5.051510)]
        geographic_coords = [(291, 607), (286, 617), (299, 625), (274, 625), (278, 651), (253, 661), (257, 685), (235, 713), (250, 712), (310, 703), (338, 680), (342, 665), (333, 617), (506, 639), (302, 580), (316, 594), (466, 612), (424, 790), (342, 754), (275, 798), (255, 835), (262, 615)]
        image_points =np.array( [(244, 499), (354, 467), (321, 375), (521, 426), (560, 326), (721, 349), (696, 288), (777, 268), (714, 249), (500, 217), (361, 227), (310, 235), (157, 316), (91, 210), (0, 564), (0, 461), (2, 248), (359, 170), (478, 187), (634, 186), (688, 190),(585, 597)] )
    else:
        image_points = np.array([])
        geographic_coords = [()]
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
                    "frame_id": x["frame_id"],
                    "time": x["time"],
                    "lat": lat,
                    "lon": lon
                }
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
    # # Crée une carte folium avec un fond de carte personnalisé
    # map = folium.Map(location=(47.3216684, 5.0521941), zoom_start=20)
    # folium.raster_layers.WmsTileLayer(
    #     url=link_map_leaflet,
    #     name='ORTHO2022_5cm',
    #     fmt='image/png',
    #     layers='0',
    #     transparent=True,
    #     overlay=True,
    #     control=True,
    # ).add_to(map)
    # folium.LayerControl().add_to(map)
    # for geo_t in geo_triangles:
    #     # Ajoute les triangles à la carte
    #     folium.Polygon(geo_t, color='green', fill=True, fill_color='green').add_to(map)
    # # Crée le chemin de la voiture
    # # retire les points qui sont à -1
    # car_geo_coordinates = [x for x ikan car_geo_coordinates if x["lat"] != -1 and x["lon"] != -1]
    # folium.PolyLine([(x["lat"], x["lon"]) for x in car_geo_coordinates], color='blue').add_to(map)
    # map.save('map.html')
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

        for lat, lon in zip(lats, lons_smoothed):
            smoothed_coordinates.append({"lat": lat[0], "lon": lon})

    return smoothed_coordinates
def main(video_name):
    video_path = f'static/video/{video_name}.mp4'
    json_path = f'static/video/json/{video_name}_user.json'

    if not os.path.exists(video_path):
        print(f"Le fichier vidéo '{video_path}' n'existe pas")
        exit()

    if not os.path.exists(json_path):
        print(f"Le fichier JSON '{json_path}' n'existe pas")
        exit()

    data = load_json_data(json_path)
    # met que 10 % de data
    data = data[:int(len(data) * 0.1)]
    image_points, geographic_coords = get_image_points_and_geo_coords(json_path)
    triangles, tri = get_triangles(image_points)
    print("Debut du convertion des données en coordonnées géographiques")
    geo_triangles = convert_image_triangles_to_geo(triangles, image_points, geographic_coords)
    id_person = data.index([x for x in data if x["Usager"] == "person"][-1])
    process_video_with_triangles(triangles, video_path, data[id_person]["data"])
    new_data = update_json_data(data, triangles, geo_triangles, tri)
    print("Debut du traitement du lissage des données")
    for item in tqdm.tqdm(new_data):
        if item["data"]:
            car_geo_coordinates = item["data"]
            item["data"] = smooth_trajectory(car_geo_coordinates)
    save_updated_json_data(json_path, new_data)
    create_map(geo_triangles, new_data[id_person]["data"])
    print(new_data[id_person]["Usager"])

if __name__ == "__main__":
    video_name = 'C7_Carnot_2024_02_13_08_48_54'
    main(video_name)
