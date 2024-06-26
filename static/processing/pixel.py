import cv2
import numpy as np

# Initialiser les listes de coordonnées géographiques et de pixels
geopoint = []
pixels = []

# Fonction de gestion du clic de souris
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Position du pixel (x, y) : ", x,", ", y)
        pixels.append((x, y))

def scroll_event(event, x, y, flags, param):
    global zoom_factor, zoomed_plan
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            zoom_factor += 0.1
        else:
            zoom_factor -= 0.1
        if zoom_factor < 0.1:
            zoom_factor = 0.1
        zoomed_plan = cv2.resize(plan, None, fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_LINEAR)
        cv2.imshow('plan', zoomed_plan)
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Position du pixel sur le plan (x, y) : ", x,", ", y)
        geopoint.append((x, y))
        cv2.circle(plan, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow('plan', plan)

# Paramètres de la caméra
focal_length = 3.15  # Distance focale en mm
aperture = 2.35      # Ouverture
angle_diagonal = 16  # Angle de vue diagonal en degrés

# Charger la vidéo
video_path = 'static\\video\\C7_Carnot_2024_02_13_14_49_00.webm'
plan_path = 'static\\plan.png'
cap = cv2.VideoCapture(video_path)
plan = cv2.imread(plan_path)
# afficher le plan
cv2.imshow('plan', plan)
# gestionnaire de clics de souris sur le plan

# Variables pour le zoom
zoom_factor = 1.0
zoomed_plan = plan.copy()
# Gestionnaire de scroll de la souris
cv2.setMouseCallback('plan', scroll_event)

print("Lecture de la vidéo...")
while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        break
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

    # Afficher les coordonnées de latitude et longitude sur la vidéo
    for i in range(len(pixels)):
        cv2.circle(undistorted_frame, pixels[i], 5, (0, 0, 255), -1)
    # Afficher la vidéo
    cv2.imshow('Video', undistorted_frame)

    # Gestionnaire de clics de souris
    cv2.setMouseCallback('Video', click_event)
    # Dessiner un point rouge sur la vidéo
    # Quitter la vidéo en appuyant sur la touche 'q'
    # Charger le plan

    if cv2.waitKey(1) & 0xFF == ord('q'):
        # afficher geo et pixel
        print("geographic_coords =", geopoint)
        print("image_points =np.array(", pixels,")")
        break
print("Fin de la lecture de la vidéo.")
cap.release()
cv2.destroyAllWindows()
