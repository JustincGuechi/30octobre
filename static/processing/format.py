import numpy as np
import cv2
import folium

# Coordonnées des points sur l'image (pixels)
image_points = np.array([[495, 217], [667, 194], [309, 234], [248, 492], [776, 298], [690, 254], [763, 213], [115, 217], [3, 284], [0, 504]], dtype=np.float32)

t1=[[3, 284], [115, 217], [248, 492]]
t2=[[115, 217], [309, 234], [248, 492]]
t3=[[115, 217], [667, 194], [309, 234]]
t4=[[309,234], [690,254], [667, 194]]
t5=[[690,254], [763, 213], [667, 194]]
t6=[[690,254], [776,298], [763, 213]]
t7=[[690, 254], [776, 298], [309, 234]]
t8=[[776, 298], [248,492], [309, 234]]
t9=[[0,504], [3,284], [248,492]]


triangles = [t1, t2, t3, t4, t5, t6, t7, t8, t9]
geographic_coords = [(47.321361, 5.051694), (47.321222, 5.051583), (47.321417, 5.051750), (47.321500, 5.051639), (47.321361, 5.051528), (47.321361, 5.051583), (47.321028, 5.051417), (47.321447, 5.052046), (47.321531, 5.051899),(47.321529, 5.051678)]
# meme triangle mais en geo a partir des coordonnées des points sur l'image
geo_t1=[[47.321531, 5.051899], [47.321447, 5.052046], [47.321500, 5.051639]]
geo_t2=[[47.321447, 5.052046], [47.321361, 5.051583], [47.321500, 5.051639]]
geo_t3=[[47.321447, 5.052046], [47.321222, 5.051583], [47.321361, 5.051750]]
geo_t4=[[47.321222, 5.051583], [47.321361, 5.051583], [47.321361, 5.051750]]
geo_t5=[[47.321361, 5.051583], [47.321361, 5.051528], [47.321500, 5.051639]]
geo_t6=[[47.321361, 5.051583], [47.321361, 5.051528], [47.321222, 5.051583]]
geo_t7=[[47.321361, 5.051583], [47.321222, 5.051583], [47.321417, 5.051750]]
geo_t8=[[47.321361, 5.051583], [47.321417, 5.051750], [47.321500, 5.051639]]
geo_t9=[[47.321529, 5.051678], [47.321531, 5.051899], [47.321500, 5.051639]]
geo_triangles = [geo_t1, geo_t2, geo_t3, geo_t4, geo_t5, geo_t6, geo_t7, geo_t8]



# application de la ffd
# alpha = ((u-u2)(v1-v2)+(v-v2)(u2-u1))/(u0-u2)(v1-v2)-(v0-v2)(u1-u2)
# beta = ((u-u2)(v2-v0)+(v-v2)(u0-u2))/(u1-u2)(v0-v2)-(v1-v2)(u0-u2)
# u et v sont les coordonnées du pixel dans l'image
# u0, v0, u1, v1, u2, v2 sont les coordonnées des points sur l'image
# baricentrique (alpha, beta, 1-alpha-beta)
# multiplication par les coordonnées géographiques des points sur l'image
# coordonnées géographiques du pixel
# latitude = alpha*lat0 + beta*lat1 + (1-alpha-beta)*lat2
# longitude = alpha*lon0 + beta*lon1 + (1-alpha-beta)*lon2

u = 75 
v = 297

t = triangles[0]
geo_t = geo_triangles[0]
min_dist = 999999999
min_index = 0

for i in range(0, 8):
    dist = abs(cv2.pointPolygonTest(np.array(triangles[i]), (u, v), True))
    if dist < min_dist:
        min_dist = dist
        min_index = i
        print(triangles[i], dist)

t = triangles[min_index]
geo_t = geo_triangles[min_index]
print(t, geo_t)
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
beta = ((u-u2)*(v2-v0)+(v-v2)*(u0-u2))/((u1-u2)*(v0-v2)-(v1-v2)*(u0-u2))

lat = alpha*lat0 + beta*lat1 + (1-alpha-beta)*lat2
lon = alpha*lon0 + beta*lon1 + (1-alpha-beta)*lon2




# # Create a map centered on the first geographic coordinate
map = folium.Map(location=[lat, lon], zoom_start=15)

# Draw the triangles on the map
folium.Polygon(geo_t1, color='green', fill=True, fill_color='green').add_to(map)
folium.Polygon(geo_t2, color='green', fill=True, fill_color='green').add_to(map)
folium.Polygon(geo_t3, color='green', fill=True, fill_color='green').add_to(map)
folium.Polygon(geo_t4, color='green', fill=True, fill_color='green').add_to(map)
folium.Polygon(geo_t5, color='green', fill=True, fill_color='green').add_to(map)
folium.Polygon(geo_t6, color='green', fill=True, fill_color='green').add_to(map)
folium.Polygon(geo_t7, color='green', fill=True, fill_color='green').add_to(map)
folium.Polygon(geo_t8, color='green', fill=True, fill_color='green').add_to(map)
folium.Marker([lat, lon], popup='Pixel Location').add_to(map)

# Save the map as an HTML file
map.save('map.html')

# # Open the video
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

# Afficher le point uv
cv2.circle(frame, (u, v), 5, (0, 0, 255), -1)

# afficher les triangles
for i in range(len(triangles)):
    cv2.polylines(frame, [np.int32(triangles[i])], True, (0,255,0), 2)

# afficher les coordonnées des pixels de tous les triangles
for i in range(len(image_points)):
    cv2.putText(frame, str(image_points[i]), (int(image_points[i][0]), int(image_points[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# Afficher le triangle sélectionné en rouge
cv2.polylines(frame, [np.int32(t)], True, (0,0,255), 2)

# Display the frame with triangles
cv2.imshow('Video with Triangles', frame)
cv2.waitKey(0)

# Release the video file and close the window
cap.release()
cv2.destroyAllWindows()

# # Coordonnées géographiques

