from flask import Flask, Response, render_template, request, jsonify,send_file
import cv2
import json
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data')
def data():
    camera = request.args.get('camera')
    heure = request.args.get('heure')
    jours = request.args.get('jours')
    mois = request.args.get('mois')
    annee = request.args.get('annee')
    
    json_file_path = f"static/video/json/annotated_Video_{jours}{mois}{annee}_{heure}H_{camera}.webm.json"
    print(f"Chargement des données JSON pour la caméra {camera}")

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    print("Données JSON chargées avec succès :", data)

    return jsonify(data)
# Je fait une route qui retourne une video du doissier static/video/ en fonction ce qui est passer en parametre heuere jours mois annee et camera voici le nomage des video : Video_160424_12H_C1.mp4
@app.route('/video', methods=['GET'])
def video():
    camera = request.args.get('camera')
    heure = request.args.get('heure')
    jours = request.args.get('jours')
    mois = request.args.get('mois')
    annee = request.args.get('annee')
    video_path = f"static\\video\\Video_{jours}{mois}{annee}_{heure}H_{camera}.mp4"
    print(video_path)
    return send_file(video_path)
    if os.path.exists(video_path):
        return Response(open(video_path, 'rb'), mimetype='video/webm')
    else:
        return "Video not found"
# voici un exemple de lien pour voir une video : http://127.0.0.1:5000/video?camera=C1&heure=12&jours=16&mois=04&annee=24
if __name__ == '__main__':
    app.run()
