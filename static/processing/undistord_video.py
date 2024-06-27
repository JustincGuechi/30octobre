import cv2
import numpy as np

# Vidéo d'entrée et de sortie
input_video_path = 'C4_Strasbourg_2024_02_13_08_00.mp4'
output_video_path = 'output.mp4'

# Ouvre la vidéo d'entrée
cap = cv2.VideoCapture(input_video_path)

# Vérifie si la vidéo s'est ouverte correctement
if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir la vidéo")
    exit()

# Récupère les dimensions de la vidéo
ret, frame = cap.read()
if not ret:
    print("Erreur: Impossible de lire la vidéo")
    exit()
h, w = frame.shape[:2]

# Paramètres initiaux
focal_length_px = w  # Distance focale approximative en pixels
camera_matrix = np.array([[focal_length_px, 0, w / 2],
                          [0, focal_length_px, h / 2],
                          [0, 0, 1]])

# Coefficients de distorsion initiaux (à ajuster)
dist_coeffs = np.array([0.0, 0.0, 0.0, 0.0, 0.0])  # k1, k2, p1, p2, k3

# Définition du codec et création de l'objet VideoWriter pour écrire la vidéo redressée
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec pour le format MP4
out = cv2.VideoWriter(output_video_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (w, h))

def on_trackbar(val):
    global dist_coeffs
    dist_coeffs[0] = (cv2.getTrackbarPos('k1', 'Control Panel') - 100) / 100.0
    dist_coeffs[1] = (cv2.getTrackbarPos('k2', 'Control Panel') - 100) / 100.0
    dist_coeffs[2] = (cv2.getTrackbarPos('p1', 'Control Panel') - 1000) / 1000.0
    dist_coeffs[3] = (cv2.getTrackbarPos('p2', 'Control Panel') - 1000) / 1000.0
    dist_coeffs[4] = (cv2.getTrackbarPos('k3', 'Control Panel') - 100) / 100.0
    print("Coefficients de distorsion : k1 = {:.2f}, k2 = {:.2f}, p1 = {:.3f}, p2 = {:.3f}, k3 = {:.2f}".format(
        dist_coeffs[0], dist_coeffs[1], dist_coeffs[2], dist_coeffs[3], dist_coeffs[4]))

# Crée une fenêtre de contrôle pour ajuster les coefficients
cv2.namedWindow('Control Panel')
cv2.createTrackbar('k1', 'Control Panel', 100, 200, on_trackbar)
cv2.createTrackbar('k2', 'Control Panel', 100, 200, on_trackbar)
cv2.createTrackbar('p1', 'Control Panel', 1000, 2000, on_trackbar)
cv2.createTrackbar('p2', 'Control Panel', 1000, 2000, on_trackbar)
cv2.createTrackbar('k3', 'Control Panel', 100, 200, on_trackbar)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Redresse l'image
    undistorted_frame = cv2.undistort(frame, camera_matrix, dist_coeffs)

    # Écrit le frame redressé dans la vidéo de sortie
    out.write(undistorted_frame)

    # Affiche les frames originales et redressées
    cv2.imshow('Original', frame)
    cv2.imshow('Undistorted', undistorted_frame)

    # Quitte la boucle si l'utilisateur appuie sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libère les ressources
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"La vidéo redressée a été enregistrée sous {output_video_path}")
