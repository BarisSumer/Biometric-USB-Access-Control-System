import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel, simpledialog
from verify_user import verify_user
from usb_control import process_disks, load_hidden_volumes, unhide_drive_windows
from logger import log_event
from encryptor import encrypt_file
import threading
import psutil
import time
import json
import os
from PIL import Image, ImageTk
import cv2
import platform

# --- USB Algılama ---
def get_removable_disks():
    disks = []
    for part in psutil.disk_partitions(all=False):
        if part.fstype and (part.device.startswith("D") or part.device.startswith("E") or part.device.startswith("F") or part.device.startswith("G")):
            disks.append(part.device)
    return disks

def detect_usb():
    # Takılı olan removable volume'ları `diskpart` ile kontrol et
    volumes = []

    with open("vol_check.txt", "w") as f:
        f.write("list volume")

    result = os.popen("diskpart /s vol_check.txt").read()
    os.remove("vol_check.txt")

    for line in result.splitlines():
        if "Removable" in line or "Çıkarılabilir" in line:
            parts = line.strip().split()
            if "Volume" in parts[0]:
                volumes.append(parts[-1])  # En sondaki harfi alır

    return volumes[0] if volumes else None

def get_internal_disks():
    internal_disks = []
    for part in psutil.disk_partitions(all=False):
        if "cdrom" in part.opts or part.fstype == '':
            continue
        if platform.system() == "Windows":
            device = part.device
            if not device.startswith("\\"):
                internal_disks.append(device)
    return internal_disks

def save_disks_to_file(disk_list, file_name="allowed_disks.json"):
    with open(file_name, "w") as f:
        json.dump(disk_list, f, indent=4)
    print(f"{file_name} dosyasına kaydedildi.")
    messagebox.showinfo("Başarılı", "Dahili diskler başarıyla kaydedildi!")

# --- Ana Uygulama ---
class USBAccessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Biyometrik USB Güvenlik Sistemi")
        self.root.geometry("500x460")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        self.title_label = tk.Label(root, text="USB Erişim Kontrol", font=("Segoe UI", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.title_label.pack(pady=10)

        self.status_label = tk.Label(root, text="USB bekleniyor...", font=("Segoe UI", 14), bg="#f0f0f0", fg="#34495e")
        self.status_label.pack(pady=10)

        self.retry_button = tk.Button(root, text="Farklı Kullanıcı", font=("Segoe UI", 12), command=self.start_verification, state="disabled", bg="#3498db", fg="white", padx=10, pady=5)
        self.retry_button.pack(pady=10)

        self.log_button = tk.Button(root, text="Logları Görüntüle", font=("Segoe UI", 10), command=self.show_logs, bg="#2ecc71", fg="white", padx=8, pady=4)
        self.log_button.pack(pady=5)

        self.screenshot_button = tk.Button(root, text="Tanınmayan Yüzler", font=("Segoe UI", 10), command=self.show_screenshots, bg="#e67e22", fg="white", padx=8, pady=4)
        self.screenshot_button.pack(pady=5)

        self.admin_button = tk.Button(root, text="Yeni Kullanıcı Ekle", font=("Segoe UI", 10), command=self.add_new_user, bg="#9b59b6", fg="white", padx=8, pady=4)
        self.admin_button.pack(pady=5)

        self.disk_button = tk.Button(root, text="Dahili Diskleri Kaydet", font=("Segoe UI", 10), command=self.save_internal_disks, bg="#34495e", fg="white", padx=8, pady=4)
        self.disk_button.pack(pady=5)

        self.start_usb_thread()

    def save_internal_disks(self):
        disks = get_internal_disks()
        save_disks_to_file(disks)

    def start_usb_thread(self):
        thread = threading.Thread(target=self.wait_for_usb)
        thread.daemon = True
        thread.start()

    def wait_for_usb(self):
        while True:
            usb_letter = detect_usb()
            if usb_letter:
                break
            time.sleep(2)

        self.status_label.config(text="USB tespit edildi.\nYüz tanıma başlatılıyor...", fg="#2980b9")
        self.start_verification()

    def start_verification(self):
        usb_disks = get_removable_disks()
        hidden = load_hidden_volumes()

        if not usb_disks and not hidden:
            self.status_label.config(text="❗ USB takılı değil. Tanıma başlatılamaz.", fg="red")
            self.retry_button.config(state="normal")
            return

        self.status_label.config(text="Kameraya bakın, tanıma başlıyor...", fg="#e67e22")
        self.retry_button.config(state="disabled")

        def run_verification():
            user = verify_user()
            if user:
                self.status_label.config(text=f"✔ Erişim verildi: {user}", fg="#27ae60")

                for hidden_letter in load_hidden_volumes():
                    unhide_drive_windows(hidden_letter)

                process_disks(user_verified=True)
                for disk in get_removable_disks():
                    log_event(user, "verified", "usb_unlocked", disk)
            else:
                self.status_label.config(text="❌ Tanınmayan kullanıcı, erişim reddedildi.", fg="#c0392b")
                process_disks(user_verified=False)
                for disk in get_removable_disks():
                    log_event("unknown", "denied", "usb_hidden", disk)

            self.retry_button.config(state="normal")

        threading.Thread(target=run_verification).start()

    def show_logs(self):
        log_win = Toplevel(self.root)
        log_win.title("Log Kayıtları")
        log_win.geometry("600x400")
        log_win.configure(bg="#ffffff")
        text_area = scrolledtext.ScrolledText(log_win, wrap=tk.WORD, font=("Segoe UI", 10))
        text_area.pack(expand=True, fill='both', padx=10, pady=10)
        try:
            with open("log.json", "r") as f:
                logs = json.load(f)
                for entry in logs:
                    line = f"[{entry['timestamp']}] {entry['user']} - {entry['status']} - {entry['action']} ({entry['disk']})\n"
                    text_area.insert(tk.END, line)
        except:
            text_area.insert(tk.END, "Log dosyası bulunamadı veya okunamadı.")

    def show_screenshots(self):
        ss_win = Toplevel(self.root)
        ss_win.title("Tanınmayan Yüzler")
        ss_win.geometry("620x500")
        ss_win.configure(bg="#ffffff")
        canvas = tk.Canvas(ss_win, bg="#ffffff")
        canvas.pack(expand=True, fill="both")
        row = 0
        col = 0
        path = "screenshots"
        if not os.path.exists(path):
            tk.Label(canvas, text="Hiç tanınmayan yüz kaydı bulunamadı.", font=("Segoe UI", 12), bg="#ffffff").pack(pady=20)
            return
        for filename in sorted(os.listdir(path), reverse=True):
            if filename.endswith(".jpg"):
                try:
                    img_path = os.path.join(path, filename)
                    img = Image.open(img_path)
                    img = img.resize((140, 140))
                    img_tk = ImageTk.PhotoImage(img)
                    panel = tk.Label(canvas, image=img_tk)
                    panel.image = img_tk
                    panel.grid(row=row, column=col, padx=10, pady=10)
                    label = tk.Label(canvas, text=filename, font=("Segoe UI", 8), bg="#ffffff")
                    label.grid(row=row + 1, column=col)
                    col += 1
                    if col > 3:
                        col = 0
                        row += 2
                except:
                    continue

    def add_new_user(self):
        name = simpledialog.askstring("Yeni Kullanıcı", "Kullanıcı adını girin:")
        if not name:
            return

        folder_path = os.path.join("encrypted_faces", name)
        os.makedirs(folder_path, exist_ok=True)

        cap = cv2.VideoCapture(0)
        messagebox.showinfo("Bilgilendirme", "Yüzünüzü kameraya gösterin.\nHer SPACE basışta bir fotoğraf çekilecek.\nESC ile kayıt işlemi bitecek.")

        photo_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            cv2.imshow("Yeni Kullanıcı Kaydı - SPACE: Çek / ESC: Çık", frame)
            key = cv2.waitKey(1)

            if key == 27:
                break

            elif key == 32:
                timestamp = int(time.time() * 1000)
                temp_path = os.path.join(folder_path, f"{timestamp}.png")
                cv2.imwrite(temp_path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                try:
                    encrypt_file(temp_path)
                    photo_count += 1
                    print(f"{name} için {photo_count}. fotoğraf kaydedildi.")
                except Exception as e:
                    print("Şifreleme hatası:", e)
                    messagebox.showerror("Hata", f"Fotoğraf şifrelenemedi: {e}")

        cap.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Kayıt Tamamlandı", f"{name} adlı kullanıcı için toplam {photo_count} fotoğraf kaydedildi.")

if __name__ == "__main__":
    root = tk.Tk()
    app = USBAccessApp(root)
    root.mainloop()




