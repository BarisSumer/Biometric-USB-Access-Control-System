from cryptography.fernet import Fernet
import os
import base64
import cv2
import numpy as np

KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_file(image_path):
    key = load_key()
    fernet = Fernet(key)

    # read image and convert to bytes via base64
    image = cv2.imread(image_path)
    _, buffer = cv2.imencode(".png", image)
    img_bytes = buffer.tobytes()
    encrypted = fernet.encrypt(img_bytes)

    with open(image_path + ".enc", "wb") as f:
        f.write(encrypted)

    os.remove(image_path)

def decrypt_file(encrypted_path, output_path):
    key = load_key()
    fernet = Fernet(key)

    with open(encrypted_path, "rb") as f:
        encrypted = f.read()
    decrypted = fernet.decrypt(encrypted)

    # decode from memory (no write needed)
    nparr = np.frombuffer(decrypted, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    cv2.imwrite(output_path, image)
