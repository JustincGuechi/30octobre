import cv2
import json
import numpy as np

def draw_zones_on_image(image_path, json_path):
    # Charger l'image
    image = cv2.imread(image_path)

    # Charger les données du fichier JSON
    with open('static/ortho.json') as f:
        data = json.load(f)
        for zone, points in data.items():
            color = tuple(np.random.randint(0, 256, 3).tolist())
            # verifie si int et ext existe
            if 'int' in points and 'ext' in points:
                points_exterieur = [np.array(points["ext"]).astype(int)]
                points_interieur = [np.array(points["int"]).astype(int)]
                cv2.polylines(image, points_exterieur, True, color, 2)
                cv2.polylines(image, points_interieur, True, color, 2)
            else:
                points = [np.array(points).astype(int)]
                cv2.polylines(image, points, True, color, 2)


    # Afficher l'image avec les zones dessinées
    cv2.imshow('Zones', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Exemple d'utilisation
image_path = 'static/plan.png'
json_path = 'static/ortho.json'
draw_zones_on_image(image_path, json_path)