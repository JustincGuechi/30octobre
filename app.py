
import os
from flask import Flask, render_template, jsonify, request, Response, send_file, session, url_for, redirect, flash
import json
from flask_restful import Api, Resource
import secrets
import re

app = Flask(__name__)
api = Api(app)
secret_key = secrets.token_hex(32)

app.secret_key = secret_key # Assurez-vous de définir une clé secrète sécurisée
app.config['SESSION_TYPE'] = 'filesystem'




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Pour simplifier, utilisons des identifiants statiques
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            flash('Connexion réussie !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Route pour déconnecter l'utilisateur
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('login'))


# Route principale pour afficher la page HTML
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

JSON_FILES_DIRECTORY = 'static/video/json'

@app.route('/get_json_for_plan', methods=['GET'])
def get_json_for_plan():
    # Récupération des paramètres passés en requête
    hour = request.args.get('hour')
    day = request.args.get('day')
    
    if not hour or not day:
        return jsonify({"error": "Both hour and day parameters are required"}), 400

    try:
        hour = int(hour) - 1  # Décrémente l'heure de 1
    except ValueError:
        return jsonify({"error": "Hour must be an integer"}), 400

    # Ajout de zéro devant les heures de 0 à 9 pour correspondre au format hh
    hour_str = f"{hour:02}"

    # Pattern pour matcher les fichiers
    pattern = re.compile(r'^[^_]+_[^_]+_\d{4}_\d{2}_' + re.escape(day) + r'_' + re.escape(hour_str) + r'_\d{2}_\d{2}_user_geo\.json$')

    matched_files = []

    # Parcours des fichiers dans le dossier
    for filename in os.listdir(JSON_FILES_DIRECTORY):
        if pattern.match(filename):
            file_path = os.path.join(JSON_FILES_DIRECTORY, filename)
            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)
                    # Ajout du nom du fichier avec les données JSON
                    timedebutseconde = int(filename.split("_")[5])*3600 + int(filename.split("_")[6])*60 + int(filename.split("_")[7])
                    matched_files.append({"Time_code_debut": timedebutseconde, "data": data})
                except json.JSONDecodeError:
                    return jsonify({"error": f"Error decoding JSON in file {filename}"}), 500
    print(len(matched_files))
    return jsonify(matched_files)

@app.route('/statistiques')
def statistiques():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('statistiques.html')



@app.route('/get_video_exist', methods=['GET'])
def get_video_exist():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    camera = request.args.get('camera')
    video_directory = os.path.join("static", "video")
    video_files = []
    list_file = os.listdir(video_directory)
    print(list_file)
    for filename in list_file:
        if filename.startswith(camera):
            video_files.append(filename)
            print(filename)
    # Trier les fichiers vidéo par heure
    sorted_files = sorted(video_files)
    date_hour_exist = []
    # C1_Thiers_2024_02_13_14_22_05
    # envoi dans is_valid_time_sequence 2 par 2 pour vérifier si les heures sont consécutives
    for i in range(1, len(sorted_files)):
        # Extraire les heures des noms de fichiers précédent et suivant
        previous_parts = sorted_files[i - 1].split('_')
        current_parts = sorted_files[i].split('_')
        # Vérifier si tous les éléments jusqu'à l'heure sont identiques
        if previous_parts[:5] != current_parts[:5]:
            break
        # Vérifier si l'heure du fichier suivant est exactement une heure de plus que celle du fichier précédent
        previous_hour = int(previous_parts[-3])
        current_hour = int(current_parts[-3])
        if current_hour == previous_hour + 1:
            date_hour_exist.append(str(current_parts[0]) + "_" + str(current_parts[1]) + "_" + str(current_parts[2]) + "_" + str(current_parts[3]) + "_" + str(current_parts[4]) + "_" + str(current_parts[5]))
        if len(date_hour_exist) == 0:
            return "No video found", 404
    return jsonify(date_hour_exist)



@app.route('/update_interaction_valider', methods=['GET'])
def update_interaction_valider():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400
 
    # Extraction de l'heure de début de l'intervalle
    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"
 
    # Extraire l'heure, la convertir en entier et lui soustraire 1
    hour_str = dayHour_split[3]
    hour_int = int(hour_str)
 
    # Formater l'heure modifiée avec un zéro devant si nécessaire
    if len(str(hour_int)) == 1:
        nvhour_int = "0" + str(hour_int)
    else:
        nvhour_int = str(hour_int)
 
    # Mettre à jour le dayHour_split avec la nouvelle heure
    dayHour_split[3] = nvhour_int
 
    dayHour_avant = "_".join(dayHour_split[:4]) + "_"
    print(dayHour_avant)
    nameprefix = find_video_file_json(camera, dayHour_avant)
    print(nameprefix)
    nameprefix = os.path.splitext(nameprefix)[0]
    json_file_path = os.path.join(f"{nameprefix}_geo_interactions.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data1 = json.load(f)  # Charge les données JSON depuis le fichier

    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400
 
    # Extraction de l'heure de début de l'intervalle
    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"
 
    # Extraire l'heure, la convertir en entier et lui soustraire 1
    hour_str = dayHour_split[3]
    hour_int = int(hour_str) - 1
 
    # Formater l'heure modifiée avec un zéro devant si nécessaire
    if len(str(hour_int)) == 1:
        nvhour_int = "0" + str(hour_int)
    else:
        nvhour_int = str(hour_int)
 
    # Mettre à jour le dayHour_split avec la nouvelle heure
    dayHour_split[3] = nvhour_int
 
    dayHour_avant = "_".join(dayHour_split[:4]) + "_"
    print(dayHour_avant)
    nameprefix = find_video_file_json(camera, dayHour_avant)
    print(nameprefix)
    nameprefix = os.path.splitext(nameprefix)[0]
    json_file_path = os.path.join(f"{nameprefix}_geo_interactions.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)  # Charge les données JSON depuis le fichier
    
    interaction_id = request.args.get('Id')
    valide = request.args.get('statut')

    
    # Mettre à jour les données appropriées
    interaction_found = False
    for interaction in data:
        if interaction['id_interaction'] == interaction_id:
            interaction['valide'] = valide
            interaction_found = True
            break
    for interaction in data1:
        if interaction['id_interaction'] == interaction_id:
            interaction['valide'] = valide
            interaction_found = True
            break
        
    if not interaction_found:
        app.logger.error("Interaction ID not found")
        return jsonify({"error": "Interaction ID not found"}), 404

    # Écrire les données mises à jour dans le fichier JSON
    try:
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=1)
    except IOError:
        app.logger.error(f"Error writing JSON to file {json_file_path}")
        return jsonify({"error": f"Error writing JSON to file {json_file_path}"}), 500

    # Exemple de traitement de données - Affichage dans la console
    app.logger.info(f"ID: {interaction_id}")
    app.logger.info(f"Validé: {valide}")

    # Retourner une réponse (par exemple, un message de succès)
    return 'Données mises à jour avec succès !'


@app.route('/update_interaction_modifier', methods=['GET'])
def update_interaction():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400
 
    # Extraction de l'heure de début de l'intervalle
    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"
    
    # Extraire l'heure, la convertir en entier et lui soustraire 1
    hour_str = dayHour_split[3]
    hour_int = int(hour_str) - 1
    hour_verif = request.args.get('hour')
    if hour_int != int(hour_verif)-1:
        hour_int = hour_int + 1
    # Formater l'heure modifiée avec un zéro devant si nécessaire
    if len(str(hour_int)) == 1:
        nvhour_int = "0" + str(hour_int)
    else:
        nvhour_int = str(hour_int)
 
    # Mettre à jour le dayHour_split avec la nouvelle heure
    dayHour_split[3] = nvhour_int
 
    dayHour_avant = "_".join(dayHour_split[:4]) + "_"
 
    nameprefix = find_video_file_json(camera, dayHour_avant)
    nameprefix = os.path.splitext(nameprefix)[0]
    json_file_path = os.path.join(f"{nameprefix}_geo_interactions.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)  # Charge les données JSON depuis le fichier


    # Traiter les données
    interaction_id = request.args.get('Id')
    interaction_time_code_debut = request.args.get('Time_code_debut')
    interaction_time_code_fin = request.args.get('Time_code_fin')
    interaction_type = request.args.get('interaction')
    commentaire = request.args.get('commentaire')
    valide = request.args.get('statut')


    # Mettre à jour les données appropriées
    for interaction in data:
        if interaction['id_interaction'] == interaction_id:
            interaction['interaction'] = interaction_type
            interaction['start_time'] = interaction_time_code_debut
            interaction['end_time'] = interaction_time_code_fin
            interaction['commentaire'] = commentaire
            break

    # Écrire les données mises à jour dans le fichier JSON
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    # Exemple de traitement de données - Affichage dans la console
    print("ID:", interaction_id)
    print("Interaction:", interaction_type)
    print("Commentaire:", commentaire)
    print("Validé:", valide)

    # Retourner une réponse (par exemple, un message de succès)
    return 'Données mises à jour avec succès !'

@app.route('/get_usagers1', methods=['GET'])
def get_usagers1():
    print("get_usager")
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400
 
    # Extraction de l'heure de début de l'intervalle
    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"
 
    # Extraire l'heure, la convertir en entier et lui soustraire 1
    hour_str = dayHour_split[3]
    hour_int = int(hour_str) - 1
 
    # Formater l'heure modifiée avec un zéro devant si nécessaire
    if len(str(hour_int)) == 1:
        nvhour_int = "0" + str(hour_int)
    else:
        nvhour_int = str(hour_int)
 
    # Mettre à jour le dayHour_split avec la nouvelle heure
    dayHour_split[3] = nvhour_int
 
    dayHour_avant = "_".join(dayHour_split[:4]) + "_"
 
    nameprefix = find_video_file_json(camera, dayHour_avant)
    nameprefix = os.path.splitext(nameprefix)[0]
    json_file_path = os.path.join(f"{nameprefix}_light.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)  # Charge les données JSON depuis le fichier
        return jsonify(data)
    else:
        return f"JSON data not found for camera={camera} and dayHour={dayHour_prefix}", 404
 
@app.route('/get_usagers2', methods=['GET'])
def get_usagers2():
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400
 
    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"
 
    nameprefix = find_video_file_json(camera, dayHour_prefix)
    nameprefix = os.path.splitext(nameprefix)[0]
    json_file_path = os.path.join(f"{nameprefix}_light.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)  # Charge les données JSON depuis le fichier
        return jsonify(data)
    else:
        return f"JSON data not found for camera={camera} and dayHour={dayHour_prefix}", 404
 
 
@app.route('/get_interactions1', methods=['GET'])
def get_interactions1():
    print("get_usager")
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400
 
    # Extraction de l'heure de début de l'intervalle
    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"
 
    # Extraire l'heure, la convertir en entier et lui soustraire 1
    hour_str = dayHour_split[3]
    hour_int = int(hour_str) - 1
 
    # Formater l'heure modifiée avec un zéro devant si nécessaire
    if len(str(hour_int)) == 1:
        nvhour_int = "0" + str(hour_int)
    else:
        nvhour_int = str(hour_int)
 
    # Mettre à jour le dayHour_split avec la nouvelle heure
    dayHour_split[3] = nvhour_int
 
    dayHour_avant = "_".join(dayHour_split[:4]) + "_"
 
    nameprefix = find_video_file_json(camera, dayHour_avant)
    nameprefix = os.path.splitext(nameprefix)[0]
    json_file_path = os.path.join(f"{nameprefix}_geo_interactions.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)  # Charge les données JSON depuis le fichier
        return jsonify(data)
    else:
        return f"JSON data not found for camera={camera} and dayHour={dayHour_prefix}", 404
 
@app.route('/get_interactions2', methods=['GET'])
def get_interactions2():
    
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400
 
    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"
 
    nameprefix = find_video_file_json(camera, dayHour_prefix)
    nameprefix = os.path.splitext(nameprefix)[0]
    print(nameprefix)
    json_file_path = os.path.join(f"{nameprefix}.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)  # Charge les données JSON depuis le fichier
        return jsonify(data)
    else:
        return f"JSON data not found for camera={camera} and dayHour={dayHour_prefix}", 404

@app.route('/delete_interaction', methods=['GET'])
def delete_interaction():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    urlVideoInteraction = request.args.get('urlVideoInteraction')
    # Récupérer l'ID de l'interaction à supprimer depuis les paramètres de la requête
    interaction_id = request.args.get('Id')

    # Charger le contenu du fichier JSON contenant les données d'interaction
    with open(urlVideoInteraction, 'r') as file:
        data = json.load(file)

    # Rechercher et supprimer l'interaction correspondante dans les données
    for interaction in data['Data']:
        if interaction['ID'] == interaction_id:
            data['Data'].remove(interaction)
            break

    # Écrire les données mises à jour dans le fichier JSON
    with open(urlVideoInteraction, 'w') as file:
        json.dump(data, file, indent=4)

    # Afficher un message dans la console pour indiquer que l'interaction a été supprimée avec succès
    print("Interaction ID:", interaction_id, "supprimée avec succès")

    # Retourner une réponse indiquant que l'interaction a été supprimée avec succès
    return 'Interaction ID {} supprimée avec succès !'.format(interaction_id)


@app.route('/create_interaction', methods=['POST'])
def create_interaction():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    urlVideoInteraction = request.args.get('urlVideoInteraction')
    # Traiter les données pour créer une nouvelle interaction
    interaction_data = request.json

    # Extraire les données de la requête JSON
    interaction_id = interaction_data.get('ID')
    time_code_debut = interaction_data.get('Time_code_debut')
    time_code_fin = interaction_data.get('Time_code_fin')
    interaction = interaction_data.get('Interaction')
    commentaire = interaction_data.get('Commentaire')
    valide = interaction_data.get('Valide')

    # Initialiser la liste des usagers
    # Traiter les données pour créer une nouvelle interactio
    usagers = []
    # Initialiser la liste des usagers
    if 'User' in interaction_data:
        # Parcourir chaque usager dans la liste des usagers fournie
        for usager in interaction_data['User']:
            # Ajouter l'ID de l'usager à la liste des usagers
            usagers.append({'ID_usager': usager.get('ID_usager')})

    print("ID des usagers :", usagers)

    # Charger les données JSON existantes à partir du fichier
    with open(urlVideoInteraction, 'r') as file:
        data = json.load(file)

        # Ajouter un nouvel objet avec les données fournies
        nouvel_objet = {
            'ID': interaction_id,
            'Time_code_debut': time_code_debut,
            'Time_code_fin': time_code_fin,
            'Interaction': interaction,
            'Usager': usagers,
            'Commentaire': commentaire,
            'Valide': valide
        }

        data['Data'].append(nouvel_objet)

    # Enregistrer la structure de données mise à jour dans le fichier JSON
    with open(urlVideoInteraction, 'w') as file:
        json.dump(data, file, indent=4)

    # Vous pouvez retourner une réponse JSON pour informer le frontend que l'interaction a été créée avec succès
    response = {'success': True, 'message': 'Nouvelle interaction créée avec succès !'}
    return jsonify(response)


def find_video_file(camera, dayHour_prefix):
    video_directory = os.path.join("static", "video")
    for filename in os.listdir(video_directory):
        if filename.startswith(camera):
            if filename.startswith(f"{camera}_{dayHour_prefix}"):
                return os.path.join(video_directory, filename)
    return None


def find_video_file_json(camera, dayHour_prefix):
    video_directory = os.path.join("static", "video", "json")
    for filename in os.listdir(video_directory):
        if filename.startswith(camera):
            if filename.startswith(f"{camera}_{dayHour_prefix}"):
                return os.path.join(video_directory, filename)
    return None


def get_last_five_characters(video_path):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    last_five = video_name[-5:]
    minutes, seconds = last_five.split('_')
    return {'minutes': minutes, 'seconds': seconds}


@app.route('/video1', methods=['GET'])
def video1():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400

    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"

    # Extraire l'heure, la convertir en entier et lui soustraire 1
    hour_str = dayHour_split[3]
    hour_int = int(hour_str) - 1

    # Formater l'heure modifiée avec un zéro devant si nécessaire
    if len(str(hour_int)) == 1:
        nvhour_int = "0" + str(hour_int)
    else:
        nvhour_int = str(hour_int)

    # Mettre à jour le dayHour_split avec la nouvelle heure
    dayHour_split[3] = nvhour_int

    dayHour_avant = "_".join(dayHour_split[:4]) + "_"

    video_past = find_video_file(camera, dayHour_avant)
    if video_past:
        if os.path.exists(video_past):
            return send_file(video_past, mimetype='video/webm')
        else:
            return f"Video not found for camera={camera} and dayHour={dayHour_prefix}", 404
    else:
        return f"No video found for camera={camera} and dayHour={dayHour_prefix}", 404


@app.route('/video2', methods=['GET'])
def video2():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400

    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"

    video_path = find_video_file(camera, dayHour_prefix)
    if video_path:
        print("Video select", video_path)
        if os.path.exists(video_path):
            return send_file(video_path, mimetype='video/webm')
        else:
            return f"Video not found for camera={camera} and dayHour={dayHour_prefix}", 404
    else:
        return f"No video found for camera={camera} and dayHour={dayHour_prefix}", 404


@app.route('/minutes_sec', methods=['GET'])
def minutes_sec():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')

    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"

    video_path = find_video_file(camera, dayHour_prefix)
    time_parts = get_last_five_characters(video_path)

    minutes = time_parts['minutes']
    seconds = time_parts['seconds']

    return jsonify({'minutes': minutes, 'seconds': seconds})


@app.route('/data1', methods=['GET'])
def data1():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400

    # Extraction de l'heure de début de l'intervalle
    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"

    # Extraire l'heure, la convertir en entier et lui soustraire 1
    hour_str = dayHour_split[3]
    hour_int = int(hour_str) - 1

    # Formater l'heure modifiée avec un zéro devant si nécessaire
    if len(str(hour_int)) == 1:
        nvhour_int = "0" + str(hour_int)
    else:
        nvhour_int = str(hour_int)

    # Mettre à jour le dayHour_split avec la nouvelle heure
    dayHour_split[3] = nvhour_int

    dayHour_avant = "_".join(dayHour_split[:4]) + "_"

    nameprefix = find_video_file_json(camera, dayHour_avant)
    nameprefix = os.path.splitext(nameprefix)[0]
    json_file_path = os.path.join(f"{nameprefix}.json")
    print(json_file_path)
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)  # Charge les données JSON depuis le fichier
        return jsonify(data)
    else:
        return f"JSON data not found for camera={camera} and dayHour={dayHour_prefix}", 404


@app.route('/data2', methods=['GET'])
def data2():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    camera = request.args.get('camera')
    dayHour = request.args.get('dayHour')
    if not camera or not dayHour:
        return "Camera or dayHour parameter is missing", 400

    # Extraction de l'heure de début de l'intervalle
    dayHour_split = dayHour.split("_")
    dayHour_prefix = "_".join(dayHour_split[:4]) + "_"

    nameprefix = find_video_file_json(camera, dayHour_prefix)
    nameprefix = os.path.splitext(nameprefix)[0]
    json_file_path = os.path.join(f"{nameprefix}.json")
    print(json_file_path)
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)  # Charge les données JSON depuis le fichier
        return jsonify(data)
    else:
        return f"JSON data not found for camera={camera} and dayHour={dayHour_prefix}", 404


@app.route('/get_video_files_btn', methods=['GET'])
def get_video_files():
    camera = request.args.get('camera')
    dayHour_prefix = request.args.get('dayHour_prefix')

    if not camera or not dayHour_prefix:
        return "Camera or dayHour_prefix parameter is missing", 400

    video_directory = os.path.join("static", "video")
    video_files = []

    for filename in os.listdir(video_directory):
        if filename.startswith(camera) and filename.startswith(dayHour_prefix):
            video_files.append(filename)

    return jsonify(video_files)


if __name__ == "__main__":
    app.run(debug=True)