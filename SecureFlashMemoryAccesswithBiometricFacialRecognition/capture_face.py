import cv2
import os

def create_user_folder(user_name):
    folder_path = os.path.join("encrypted_faces", user_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def capture_face(user_name):
    folder = create_user_folder(user_name)
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Yüzünüzü Ortalayın ve SPACE'e Basın", cv2.WINDOW_NORMAL)

    img_counter = 1

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kamera açılamadı.")
            break

        cv2.imshow("Yüzünüzü Ortalayın ve SPACE'e Basın", frame)
        key = cv2.waitKey(1)

        if key % 256 == 27:  # ESC tuşu
            print("Çıkılıyor.")
            break
        elif key % 256 == 32:  # SPACE tuşu
            img_name = f"{folder}/face{img_counter}.jpg"
            cv2.imwrite(img_name, frame)
            print(f"{img_name} kaydedildi.")
            img_counter += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    name = input("Kullanıcı adını girin: ")
    capture_face(name)
