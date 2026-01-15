from deepface import DeepFace
import os
import cv2
import time
from encryptor import decrypt_file

def verify_user():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Kameraya Bakın - SPACE: Çek / ESC: Çık", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Kameraya Bakın - SPACE: Çek / ESC: Çık", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            print("Kullanıcı işlemi iptal etti.")
            cap.release()
            cv2.destroyAllWindows()
            return None

        elif key == 32:  # SPACE
            for _ in range(5):
                ret, frame = cap.read()
            img_path = "temp.png"
            cv2.imwrite(img_path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
            print("Fotoğraf çekildi, doğrulama başlıyor...")
            break

    cap.release()
    cv2.destroyAllWindows()

    dataset_path = "encrypted_faces"
    for user in os.listdir(dataset_path):
        user_folder = os.path.join(dataset_path, user)
        match_count = 0  # başarılı eşleşme sayısı

        for enc_file in os.listdir(user_folder):
            if not enc_file.endswith(".enc"):
                continue

            enc_path = os.path.join(user_folder, enc_file)
            temp_decrypted_path = "decrypted.png"

            try:
                decrypt_file(enc_path, temp_decrypted_path)

                result = DeepFace.verify(
                    img1_path=img_path,
                    img2_path=temp_decrypted_path,
                    model_name="Facenet512",
                    distance_metric="cosine",
                    enforce_detection=True
                )
                os.remove(temp_decrypted_path)

                if result["verified"] or result["distance"] < 0.45:
                    match_count += 1
                    if match_count >= 2:  # 2 eşleşme yeterli
                        print(f"Kullanıcı tanındı: {user}")
                        os.remove(img_path)
                        return user

            except Exception as e:
                continue

    # tanınmazsa
    os.remove(img_path)
    print("Kullanıcı tanınmadı.")
    os.makedirs("screenshots", exist_ok=True)
    screenshot_path = os.path.join("screenshots", f"{int(time.time())}.jpg")
    cv2.imwrite(screenshot_path, frame)
    print(f"Tanınmayan yüz kaydedildi: {screenshot_path}")
    return None
