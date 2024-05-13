from flask import Flask, Response, render_template, request, jsonify
import cv2
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

# Je fait une route qui retourne une video du doissier static/video/ en fonction ce qui est passer en parametre heuere jours mois annee et camera voici le nomage des video : Video_160424_12H_C1.mp4
@app.route('/video', methods=['GET'])
def video():
    camera = request.args.get('camera')
    heure = request.args.get('heure')
    jours = request.args.get('jours')
    mois = request.args.get('mois')
    annee = request.args.get('annee')
    video_path = f"static/video/annotated_Video_{jours}{mois}{annee}_{heure}H_{camera}.webm"
    print(video_path)
    if os.path.exists(video_path):
        return Response(open(video_path, 'rb'), mimetype='video/webm')
    else:
        return "Video not found"
# voici un exemple de lien pour voir une video : http://127.0.0.1:5000/video?camera=C1&heure=12&jours=16&mois=04&annee=24
if __name__ == '__main__':
    app.run()
