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


def main():
    # Coordonnées des points sur l'image (pixels)
    image_points = np.array([[495, 217], [667, 194], [309, 234], [248, 492], [776, 298], [690, 254], [763, 213], [115, 217], [3, 284], [0, 504], [261, 173], [361, 177], [564, 568], [142, 340], [561, 324],[ 568, 220], [327, 373], [675, 289], [767, 262]], dtype=np.float32)


    # donne la liste des triangles de Delaunay
    tri = Delaunay(image_points).simplices
    triangles = image_points[tri]

    geographic_coords = [(47.321361, 5.051694), (47.321222, 5.051583), (47.321417, 5.051750), (47.321500, 5.051639), (47.321361, 5.051528), (47.321361, 5.051583), (47.321125, 5.051428), (47.321447, 5.052046), (47.321563, 5.051865),(47.321529, 5.051678), (47.321286, 5.052094), (47.321300, 5.051900), (47.321475, 5.051601), (47.321483, 5.051722), (47.321429, 5.051628),(47.321346, 5.051657), (47.321464, 5.051666),(47.321390, 5.051593),(47.321318, 5.051514)]

    # faire que les triangles correspondent aux coordonnées géographiques
    geo_triangles = []
    for t in triangles:
        geo_t = []
        for p in t:
            geo_t.append(geographic_coords[np.where((image_points == p).all(axis=1))[0][0]])
        geo_triangles.append(geo_t)

    # Load the JSON file

    with open('./static/video/json/annotated_Alyce_ICT-1287_2024-02-16_165010_194.webm.json') as f:
        data = json.load(f)

    # Extract the coordinates for the first car
    car_data = next(item for item in data if item["Usager"] == "person" and item["ID"] == 89)
    car_coordinates = [(item["x"], item["y"], item["h"], item["w"]) for item in car_data["data"]]

    # Convert the car coordinates to numpy array
    car_points = np.array(car_coordinates, dtype=np.float32)

    # edit car_points doit être en bas au millieu de la boite
    car_points[:, 1] = car_points[:, 1] + car_points[:, 2] / 2

    # Calculate the geographic coordinates for each car point
    car_geo_coordinates = []
    for p in car_points:
        u = p[0]
        v = p[1]
        lat, lon = calculate_geographic_coordinates(u, v, triangles, geo_triangles)
        car_geo_coordinates.append((lat, lon))

    # fait le trajet de la voiture sur une carte
    map = folium.Map(location=car_geo_coordinates[0], zoom_start=15)
    folium.PolyLine(locations=car_geo_coordinates, color='red').add_to(map)
    folium.Marker(car_geo_coordinates[0], popup='Start').add_to(map)
    folium.Marker(car_geo_coordinates[-1], popup='End').add_to(map)
    for geo_t in geo_triangles:
        folium.Polygon(geo_t, color='green', fill=True, fill_color='green').add_to(map)
    map.save('map.html')
    cap = cv2.VideoCapture('static\\video\\Alyce_ICT-1287_2024-02-16_165010_194.mp4')

    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error opening video file")
        exit()

    # Read the first frame of the video
    ret, frame = cap.read()

    # Check if the frame was read successfully
    if not ret:
        print("Error reading video frame")
        exit()

    # # Afficher le point uv
    # cv2.circle(frame, (u, v), 5, (0, 0, 255), -1)

    # afficher les triangles de Delaunay
    for t in triangles:
        t = t.astype(int)
        cv2.polylines(frame, [t], True, (0, 255, 0), 2)

    # # afficher les coordonnées des pixels de tous les triangles
    # for i in range(len(image_points)):
    #     cv2.putText(frame, str(image_points[i]), (int(image_points[i][0]), int(image_points[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    # affiche tous les triangles selectionner par calculat_geographic_coordinates

    # affiche les déplacement de la voiture en pixel
    for i in range(len(car_points) - 1):
        cv2.arrowedLine(frame, (int(car_points[i][0]), int(car_points[i][1])), (int(car_points[i+1][0]), int(car_points[i+1][1])), (0, 0, 255), 2)



    # Display the frame with triangles
    cv2.imshow('Video with Triangles', frame)
    cv2.waitKey(0)

    # Release the video file and close the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


# # # Create a map centered on the first geographic coordinate
# map = folium.Map(location=[lat, lon], zoom_start=15)

# # Draw the triangles on the map
# for geo_t in geo_triangles:
#     folium.Polygon(geo_t, color='green', fill=True, fill_color='green').add_to(map)
# folium.Marker([lat, lon], popup='Pixel Location').add_to(map)

# # Save the map as an HTML file
# map.save('map.html')

# # Open the video


# # Coordonnées géographiques


# t1=[[3, 284], [115, 217], [248, 492]]
# t2=[[115, 217], [309, 234], [248, 492]]
# t3=[[115, 217], [667, 194], [309, 234]]
# t4=[[309, 234], [690, 254], [667, 194]]
# t5=[[690, 254], [763, 213], [667, 194]]
# t6=[[690, 254], [776, 298], [763, 213]]
# t7=[[690, 254], [776, 298], [309, 234]]
# t8=[[776, 298], [248, 492], [309, 234]]
# t9=[[0, 504], [3, 284], [248, 492]]
# t10=[[261, 173], [115, 217], [361, 177]]
# t11=[[361, 177], [115, 217], [667, 194]]
# triangles = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11]
# meme triangle mais en geo a partir des coordonnées des points sur l'image
# geo_t1=[[47.321531, 5.051899], [47.321447, 5.052046], [47.321500, 5.051639]]
# geo_t2=[[47.321447, 5.052046], [47.321361, 5.051583], [47.321500, 5.051639]]
# geo_t3=[[47.321447, 5.052046], [47.321222, 5.051583], [47.321361, 5.051750]]
# geo_t4=[[47.321222, 5.051583], [47.321361, 5.051583], [47.321361, 5.051750]]
# geo_t5=[[47.321361, 5.051583], [47.321361, 5.051528], [47.321500, 5.051639]]
# geo_t6=[[47.321361, 5.051583], [47.321361, 5.051528], [47.321222, 5.051583]]
# geo_t7=[[47.321361, 5.051583], [47.321222, 5.051583], [47.321417, 5.051750]]
# geo_t8=[[47.321361, 5.051583], [47.321417, 5.051750], [47.321500, 5.051639]]
# geo_t9=[[47.321529, 5.051678], [47.321531, 5.051899], [47.321500, 5.051639]]
# geo_t10=[[47.321286, 5.052094], [47.321447, 5.052046], [47.321300, 5.051900]]
# geo_t11=[[47.321300, 5.051900], [47.321447, 5.052046], [47.321361, 5.051583]]
# geo_triangles = [geo_t1, geo_t2, geo_t3, geo_t4, geo_t5, geo_t6, geo_t7, geo_t8, geo_t9, geo_t10, geo_t11]