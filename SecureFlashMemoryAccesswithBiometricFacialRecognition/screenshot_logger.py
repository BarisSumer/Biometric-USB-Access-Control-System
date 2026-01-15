import cv2
import os
from datetime import datetime

def save_unknown_face(image):
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{folder}/unknown_{timestamp}.jpg"

    cv2.imwrite(filename, image)
    print(f"📸 Tanınmayan yüz kaydedildi: {filename}")
