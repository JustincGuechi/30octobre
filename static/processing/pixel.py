import cv2
import pyperclip

# Fonction de gestion du clic de souris
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Position du pixel (x, y) : ", x,", ", y)
        pyperclip.copy(f",[{x}, {y}]")
        color = frame[y, x]
        print("Valeur du pixel (BGR) : ", color)

# Charger la vidéo
video_path = 'static\\video\\C1_Thiers\\C1_Thiers_2024_02_13_14_22_05.mp4'
cap = cv2.VideoCapture(video_path)

print("Lecture de la vidéo...")
while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        break

    # Afficher la vidéo
    cv2.imshow('Video', frame)

    # Gestionnaire de clics de souris
    cv2.setMouseCallback('Video', click_event)

    # Quitter la vidéo en appuyant sur la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
print("Fin de la lecture de la vidéo.")
cap.release()
cv2.destroyAllWindows()