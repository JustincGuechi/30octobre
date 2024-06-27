import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import CubicHermiteSpline

hermite = np.array([
    [2, -3, 0, 1],
    [1, -2, 1, 0],
    [-2, 3, 0, 0],
    [1, -1, 0, 0]
])
control_T = np.array([
    [0],
    [2],
    [0],
    [0]
])

# Charger les données à partir du fichier JSON
with open('tourne_en_round_annoted.mp4.json', 'r') as f:
    data = json.load(f)

# Nombre de points interpolés entre chaque paire de points de contrôle
num_interp_points = 100

results = {}  # Dictionnaire pour stocker les résultats avec ID et temps associés

all_velocities = []

# Parcourir les objets dans les données
for obj in data:
    obj_id = obj['ID']  # ID de l'objet
    # Récupérer les coordonnées x, y et le temps de chaque frame
    x_coords = [frame['x']+frame['w']/2 for frame in obj['data']]
    y_coords = [frame['y']+frame['h']/2 for frame in obj['data']]
    time_coords = [frame['frame_id'] for frame in obj['data']]

    obj_results = []  # Liste pour stocker les résultats associés à cet objet

    # Calculer les tangentes T1
    tangents = []
    velocities = []

    for i in range(len(x_coords)):
        if i == 0:
            # Cas du premier point de contrôle
            t1_x = x_coords[i + 1] - x_coords[i]
            t1_y = y_coords[i + 1] - y_coords[i]
        elif i == len(x_coords) - 1:
            # Cas du dernier point de contrôle
            t1_x = x_coords[i] - x_coords[i - 1]
            t1_y = y_coords[i] - y_coords[i - 1]
        else:
            # Cas des points de contrôle intermédiaires
            t1_x = (x_coords[i + 1] - x_coords[i - 1]) / 2
            t1_y = (y_coords[i + 1] - y_coords[i - 1]) / 2

        tangents.append((t1_x, t1_y))

    for i in range(len(x_coords)):
        if i == 0:
            # Cas du premier point de contrôle
            v_x = x_coords[i + 1] - x_coords[i]/ 2
            v_y = y_coords[i + 1] - y_coords[i]/ 2
        elif i == len(x_coords) - 1:
            # Cas du dernier point de contrôle
            v_x = x_coords[i] - x_coords[i - 1]/ 2
            v_y = y_coords[i] - y_coords[i - 1]/ 2
        else:
            # Cas des points de contrôle intermédiaires
            v_x = (x_coords[i + 1] - x_coords[i - 1]) / 2
            v_y = (y_coords[i + 1] - y_coords[i - 1]) / 2
        velocity = np.sqrt(v_x ** 2 + v_y ** 2)  # Calcul de la vitesse totale

        velocities.append(velocity)

    all_velocities.append((obj_id, velocities))

    # Parcourir les points de contrôle et leurs tangentes par groupe de 4
    for i in range(0, len(x_coords) - 1, 1):
        # Extraire le groupe de 4 points (P0, T0, P1, T1)
        p0 = np.array([x_coords[i]])
        t0 = np.array([tangents[i][0]])  # Assumant que le temps pour les tangentes est 0
        p1 = np.array([x_coords[i + 1]])
        t1 = np.array([tangents[i + 1][0]])  # Assumant que le temps pour les tangentes est 0

        # Regrouper les points et tangentes dans une matrice de contrôle
        control_points = np.array([p0, t0, p1, t1])

        rotation_X = np.dot( np.transpose(control_points), np.matmul(hermite, control_T) )

        # Extraire le groupe de 4 points (P0, T0, P1, T1)
        p0 = np.array([y_coords[i]])
        t0 = np.array([tangents[i][1]])  # Assumant que le temps pour les tangentes est 0
        p1 = np.array([y_coords[i + 1]])
        t1 = np.array([tangents[i + 1][1]])  # Assumant que le temps pour les tangentes est 0

        # Regrouper les points et tangentes dans une matrice de contrôle
        control_points = np.array([p0, t0, p1, t1])

        rotation_Y = np.dot(np.transpose(control_points), np.matmul(hermite, control_T))

        # Ajouter les nouvelles données à chaque frame
        obj['data'][i]['rotation_X'] = rotation_X[0][0]
        obj['data'][i]['rotation_Y'] = rotation_Y[0][0]
        obj['data'][i]['vitesse'] = velocities[i]

# Écrire les données mises à jour dans le fichier JSON
with open('tourne_en_round_annoted.mp4.json', 'w') as f:
    json.dump(data, f, indent=4)

# Afficher les résultats
for obj_id, obj_results in results.items():
    print(f"Objet {obj_id} - Résultats:")
    for time, rotation_x, rotation_y in obj_results['rotation_results']:
        print(f"Temps : {time}, Rotation X : {rotation_x}, Rotation Y : {rotation_y}")

# Afficher les vitesses pour chaque objet
for obj_id, velocities in all_velocities:
    print(f"Objet {obj_id} - Vitesses en pixels par frame:")
    for i, velocity in enumerate(velocities):
        print(f"Point {i+1}: {velocity} pixels par frame")

# Afficher les résultats sous forme de graphique
for obj_id, obj_results in results.items():
    fig, axs = plt.subplots(2)
    fig.suptitle(f"Objet {obj_id} - Rotations X et Y")

    times = [time for time, rotation_x, rotation_y in obj_results['rotation_results']]
    rot_x = [rotation_x for time, rotation_x, rotation_y in obj_results['rotation_results']]
    rot_y = [rotation_y for time, rotation_x, rotation_y in obj_results['rotation_results']]

    axs[0].set_title("Rotation X")
    axs[0].plot(times, rot_x)

    axs[1].set_title("Rotation Y")
    axs[1].plot(times, rot_y)

    plt.show()
