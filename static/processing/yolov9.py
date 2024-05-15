from collections import defaultdict
import cv2
import json
import numpy as np
import torch
from collections import Counter
 
from ultralytics import YOLO
 
 
# Load the YOLOv8 model
def load_model():
    model = YOLO('yolov8n.pt').to('cpu')
    # model = YOLO('yolov9e.pt')
    return model
 
 
# Process a single video frame
def process_frame(cap, model, frame, frame_id, track_history, track_history_with_label):
    results = model.track(frame, persist=True)
    if len(results) > 0:
        b = results[0].boxes
        if len(b) > 0:
            boxes = b.xywh.cpu()
            labels = b.cls.int().cpu().tolist()
            if b.id is not None:
                track_ids = b.id.int().cpu().tolist()
            else:
                track_ids = []
        else:
            boxes = []
            labels = []
            track_ids = []
 
        annotated_frame = results[0].plot()
 
        for box, label, track_id in zip(boxes, labels, track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track_with = track_history_with_label[track_id]
 
            track.append((float(x), float(y), label))
            track.append((float(x), float(y), label))
 
            label_name = model.names[label]
 
            current_time = cap.get(cv2.CAP_PROP_POS_MSEC)
 
            track_history_with_label[track_id].append(
                (float(x), float(y), float(w), float(h), frame_id, label_name, current_time))
 
            if len(track) > 30:
                track.pop(0)
 
    return annotated_frame
 
 
# Calculate the most frequent label for each track ID
def calculate_most_frequent_labels(track_history_with_label):
    most_frequent_labels = {}
    for track_id, track in track_history_with_label.items():
        labels = [point[5] for point in track]
        most_common_label = Counter(labels).most_common(1)[0][0]
        most_frequent_labels[track_id] = most_common_label
    return most_frequent_labels
 
 
# Replace the labels in the track history with the most frequent label
def replace_labels(track_history_with_label, most_frequent_labels):
    for track_id, track in track_history_with_label.items():
        most_common_label = most_frequent_labels[track_id]
        for i, point in enumerate(track):
            point_list = list(point)
            point_list[5] = most_common_label
            track[i] = tuple(point_list)
 
def save_track_data_to_json(track_history_with_label,output_video_path):
    def convert_ms_to_s(ms):
        seconds = ms / 1000  # Convertir les millisecondes en secondes
        return seconds
 
    # Création de la liste de dictionnaires
    track_dict = []
    track_dict_light = []
 
    for track_id, track in track_history_with_label.items():
        label = track[0][5]  # Obtenir le label à partir du premier élément de la piste
        time_debut = convert_ms_to_s( track[0][6])  # Obtenir le time_code_debut à partir du premier élément de la piste
        time_fin = convert_ms_to_s(track[-1][6]) # Obtenir le time_code_fin à partir du dernier élément de la piste
 
        track_data = [
            {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "frame_id": frame_id,
                "time": time
            } for x, y, w, h, frame_id, label, time in track
        ]
 
        track_info = {
            "ID": track_id,
            "Usager": label,
            "Datetime": time_debut,  # Utiliser time_debut ici, car il semble que vous vouliez la même valeur pour Datetime et Time_code_debut
            "Time_code_debut": time_debut,
            "Time_code_fin": time_fin,
            "data": track_data
        }
        track_info_light = {
            "ID": track_id,
            "Usager": label,
            "Datetime": time_debut,  # Utiliser time_debut ici, car il semble que vous vouliez la même valeur pour Datetime et Time_code_debut
            "Time_code_debut": time_debut,
            "Time_code_fin": time_fin,
        }
        track_dict_light.append(track_info_light)
        track_dict.append(track_info)
 
    # Enregistrement des données au format JSON dans le fichier
    link = output_video_path.split(".")[0]
    with open( link + ".json", "w") as fichier_json:
        json.dump(track_dict, fichier_json, indent=2)
 
    # Enregistrement des données au format JSON dans le fichier
    with open(link +"_light.json", "w") as fichier_json:
        json.dump(track_dict_light, fichier_json, indent=2)
 
 
def annotate_video(track_history_with_label, video_path, output_video_path):
    # Open the original video file for writing annotated video
    cap = cv2.VideoCapture(video_path)
 
    # Define the codec and create VideoWriter object for annotated video
    fourcc = cv2.VideoWriter_fourcc(*'VP80')  # Use VP9 codec for WebM
    output_video = cv2.VideoWriter(output_video_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))
 
    frame_id = 0
    # Loop through the original video frames to add bounding boxes and labels
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
 
        if success:
            # Draw bounding boxes and labels on the frame
            for track_id, track in track_history_with_label.items():
                for obj in track:
                    x, y, w, h, frame_id_, label_name,  _ = obj
 
                    if frame_id_ == frame_id :
                        if (label_name == "car"):
                            # Draw the bounding box around the object
                            cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),
                                          (255, 0, 0), 2)
 
                            # Draw the label of the detected object
                            cv2.putText(frame, 'Voiture', (int(x - w / 2), int(y - h / 2) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.9,
                                        (255, 0, 0), 2)
                        elif (label_name == "truck"):
                            # Draw the bounding box around the object
                            cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),
                                          (0, 0, 255), 2)
 
                            # Draw the label of the detected object
                            cv2.putText(frame, 'Camion', (int(x - w / 2), int(y - h / 2) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.9,
                                        (0, 0, 255), 2)
                        elif (label_name == "bus"):
                            # Draw the bounding box around the object
                            cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),
                                          (255, 255, 0), 2)
 
                            # Draw the label of the detected object
                            cv2.putText(frame, 'Bus', (int(x - w / 2), int(y - h / 2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                        (255, 255, 0), 2)
                        elif (label_name == "person"):
                            # Draw the bounding box around the object
                            cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),
                                          (0, 255, 0), 2)
 
                            # Draw the label of the detected object
                            cv2.putText(frame, 'Pieton', (int(x - w / 2), int(y - h / 2) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.9,
                                        (0, 255, 0), 2)
                        elif (label_name == "bicycle"):
                            # Draw the bounding box around the object
                            cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),
                                          (255, 0, 255), 2)
 
                            # Draw the label of the detected object
                            cv2.putText(frame, 'Velo', (int(x - w / 2), int(y - h / 2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                        (255, 0, 255), 2)
                        elif (label_name == "motorcycle"):
                            # Draw the bounding box around the object
                            cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),
                                          (0, 255, 255), 2)
 
                            # Draw the label of the detected object
                            cv2.putText(frame, 'Moto', (int(x - w / 2), int(y - h / 2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                        (0, 255, 255), 2)
 
            # Write the annotated frame to the output video
            output_video.write(frame)
            frame_id = frame_id + 1
        else:
            # Break the loop if the end of the video is reached
            break
 
    # Release the video capture object and
# Main function to process the video
def process_video(video_path):
    model = load_model()
 
    cap = cv2.VideoCapture(video_path)
 
    output_video_path = f"annotated_{video_path.split('.')[0]}.webm"
 
    track_history = defaultdict(lambda: [])
    track_history_with_label = defaultdict(lambda: [])
 
    frame_id = 0
 
    while cap.isOpened():
        success, frame = cap.read()
 
        if success:
            annotated_frame = process_frame(cap, model, frame, frame_id, track_history, track_history_with_label)
 
            cv2.imshow("YOLOv8 Tracking", annotated_frame)
 
 
            frame_id = frame_id + 1
 
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break
 
    most_frequent_labels = calculate_most_frequent_labels(track_history_with_label)
    replace_labels(track_history_with_label, most_frequent_labels)
 
    save_track_data_to_json(track_history_with_label,output_video_path)
    print_track_history(track_history_with_label)
 
    cap.release()
 
    annotate_video(track_history_with_label, video_path, output_video_path)
 
 
# Print the updated track history
def print_track_history(track_history_with_label):
    for track_id, track in track_history_with_label.items():
        print("Track ID:", track_id)
        for point in track:
            x, y, w, h, frame_id, label, time = point
            print("  x : ", x, " y : ", y, " w : ", w, " h : ", h, "frame_id", frame_id, "   Label:", label, "   Time:",
                  time)
 
 
# Run the script
process_video("Alyce_ICT-1287_2024-02-16_165010_194.mp4")