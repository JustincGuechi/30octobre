import numpy as np
import cv2
import folium
from scipy.spatial import Delaunay
import json

def calculate_geographic_coordinates(u, v, triangles, geo_triangles):
    min_dist = 999999999
    min_index = 0

    # Check if the point is inside any triangle
    for i in range(len(triangles)):
        if cv2.pointPolygonTest(np.array(triangles[i]), (u, v), False) >= 0:
            min_index = i
            break
        dist = abs(cv2.pointPolygonTest(np.array(triangles[i]), (u, v), True))
        if dist < min_dist:
            min_dist = dist
            min_index = i

    t = triangles[min_index]
    geo_t = geo_triangles[min_index]

    t = triangles[min_index]
    geo_t = geo_triangles[min_index]

    u0 = t[0][0]
    v0 = t[0][1]
    u1 = t[1][0]
    v1 = t[1][1]
    u2 = t[2][0]
    v2 = t[2][1]

    lat0 = geo_t[0][0]
    lon0 = geo_t[0][1]
    lat1 = geo_t[1][0]
    lon1 = geo_t[1][1]
    lat2 = geo_t[2][0]
    lon2 = geo_t[2][1]

    alpha = ((u-u2)*(v1-v2)+(v-v2)*(u2-u1))/((u0-u2)*(v1-v2)-(v0-v2)*(u1-u2))
    beta = ((u-u2)*(v2-v0)+(v-v2)*(u0-u2))/((u0-u2)*(v1-v2)-(v0-v2)*(u1-u2))

    lat = alpha*lat0 + beta*lat1 + (1-alpha-beta)*lat2
    lon = alpha*lon0 + beta*lon1 + (1-alpha-beta)*lon2

    return lat, lon

def load_json_data(link):
    with open(link) as f:
        data = json.load(f)
    return data

def get_image_points_and_geo_coords(link):
    if 'C1_Thiers' in link:
        image_points = np.array([[756, 538],[319, 597],[716, 418],[317, 442], [538, 330], [452, 313],[434, 338],[344, 311],[244, 326],[188, 332],[114, 343],[15, 399],[784, 380],[753, 313],[643, 276],[450, 261],[303, 279]], dtype=np.float32)
        geographic_coords = [(47.321974, 5.051581),(47.322062, 5.051542),(47.321946, 5.051642),(47.322039, 5.051642),(47.321968, 5.051779), (47.322000, 5.051837),(47.322012, 5.051763),(47.322062, 5.051870),(47.322108, 5.051819),(47.322133, 5.051782),(47.322163, 5.051751),(47.322147, 5.051638),(47.321888, 5.051663),(47.321747, 5.051851),(47.321730, 5.052165),(47.321969, 5.052695),(47.322140, 5.052161)]
    elif 'C7_Carnot' in link:
        image_points = np.array([[495, 217], [667, 194], [309, 234], [248, 492], [776, 298], [690, 254], [763, 213], [115, 217], [3, 284], [0, 504], [261, 173], [361, 177], [564, 568], [142, 340], [561, 324],[ 568, 220], [327, 373], [675, 289], [767, 262]], dtype=np.float32)
        geographic_coords = [(47.321361, 5.051694), (47.321222, 5.051583), (47.321417, 5.051750), (47.321500, 5.051639), (47.321361, 5.051528), (47.321361, 5.051583), (47.321125, 5.051428), (47.321447, 5.052046), (47.321563, 5.051865),(47.321529, 5.051678), (47.321286, 5.052094), (47.321300, 5.051900), (47.321475, 5.051601), (47.321483, 5.051722), (47.321429, 5.051628),(47.321346, 5.051657), (47.321464, 5.051666),(47.321390, 5.051593),(47.321318, 5.051514)]
    else:
        image_points = np.array([])
        geographic_coords = [()]
    return image_points, geographic_coords

def get_triangles(image_points):
    tri = Delaunay(image_points).simplices
    triangles = image_points[tri]
    return triangles

def convert_image_triangles_to_geo(triangles, image_points, geographic_coords):
    geo_triangles = []
    for t in triangles:
        geo_t = []
        for p in t:
            geo_t.append(geographic_coords[np.where((image_points == p).all(axis=1))[0][0]])
        geo_triangles.append(geo_t)
    return geo_triangles

def update_json_data(data, triangles, geo_triangles):
    new_data = []
    for item in data:
        print(item["ID"])
        car_data = item["data"]
        if car_data:
            car_coordinates = [(x["x"], x["y"], x["h"], x["w"]) for x in car_data]
            car_points = np.array(car_coordinates, dtype=np.float32)
            car_points[:, 1] = car_points[:, 1] + car_points[:, 2] / 2
            car_geo_coordinates = []
            for p in car_points:
                u = p[0]
                v = p[1]
                lat, lon = calculate_geographic_coordinates(u, v, triangles, geo_triangles)
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
    link = link.replace('.json', '_geo.json')
    with open(link, 'w') as f:
        json.dump(new_data, f, indent=4)

def create_map(geo_triangles, car_geo_coordinates):
    map = folium.Map(location=(car_geo_coordinates[0]["lat"], car_geo_coordinates[0]["lon"]), zoom_start=15)
    for geo_t in geo_triangles:
        folium.Polygon(geo_t, color='green', fill=True, fill_color='green').add_to(map)
    # créer le chemin de la voiture car_geo_coordinates
    folium.PolyLine([(x["lat"], x["lon"]) for x in car_geo_coordinates], color='blue').add_to(map)
    map.save('map.html')

def process_video_with_triangles(triangles):

    cap = cv2.VideoCapture('static\\video\\C1_Thiers\\C1_Thiers_2024_02_13_14_22_05.mp4')

    if not cap.isOpened():
        print("Error opening video file")
        exit()

    ret, frame = cap.read()

    if not ret:
        print("Error reading video frame")
        exit()

    for t in triangles:
        t = t.astype(int)
        cv2.polylines(frame, [t], True, (0, 255, 0), 2)

    cv2.imshow('Video with Triangles', frame)
    cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()

def main():
    link = 'static/video/C1_Thiers/json/C1_Thiers_2024_02_13_14_22_05_user.json'
    data = load_json_data(link)
    image_points, geographic_coords = get_image_points_and_geo_coords(link)
    triangles = get_triangles(image_points)
    geo_triangles = convert_image_triangles_to_geo(triangles, image_points, geographic_coords)
    new_data = update_json_data(data, triangles, geo_triangles)
    save_updated_json_data(link, new_data)
    create_map(geo_triangles, new_data[300]["data"])
    process_video_with_triangles(triangles)

if __name__ == "__main__":
    main()
