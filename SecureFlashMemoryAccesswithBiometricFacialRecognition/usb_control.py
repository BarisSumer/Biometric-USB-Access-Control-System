import psutil
import json
import os
import subprocess
from logger import log_event
from datetime import datetime

def load_allowed_disks():
    with open("allowed_disks.json", "r") as f:
        return json.load(f)

def load_hidden_volumes():
    if os.path.exists("hidden_volumes.json"):
        try:
            with open("hidden_volumes.json", "r") as f:
                content = f.read().strip()
                if content == "":
                    return []
                return json.loads(content)
        except:
            return []
    return []

def save_hidden_volumes(hidden_list):
    with open("hidden_volumes.json", "w") as f:
        json.dump(hidden_list, f, indent=4)

def get_removable_volumes():
    volumes = []
    subprocess.run("echo list volume | diskpart > volume_output.txt", shell=True)

    with open("volume_output.txt", "r") as f:
        lines = f.readlines()

    for line in lines:
        if "Removable" in line or "Çıkarılabilir" in line:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1].isdigit():
                volumes.append(parts[1])

    if os.path.exists("volume_output.txt"):
        os.remove("volume_output.txt")

    return volumes

def hide_drive_windows(letter):
    print(f"{letter}: USB sürücüsü gizleniyor...")

    script = f"""
select volume {letter}
remove letter={letter}
"""
    with open("hide_drive.txt", "w") as f:
        f.write(script)
    result = os.system("diskpart /s hide_drive.txt")
    os.remove("hide_drive.txt")

    if result == 0:
        hidden = load_hidden_volumes()
        if letter not in hidden:
            hidden.append(letter)
            save_hidden_volumes(hidden)
            #log_event("unknown", "denied", "usb_hidden", letter)
        print(f"{letter}: erişim engellendi.")
    else:
        print(f"{letter}: erişim engellenemedi.")

def unhide_drive_windows(letter):
    print(f"{letter}: USB sürücüsü aranıyor...")

    volumes = get_removable_volumes()
    for volume_num in volumes:
        script = f"""
select volume {volume_num}
assign letter={letter}
"""
        with open("unhide_drive.txt", "w") as f:
            f.write(script)
        result = os.system("diskpart /s unhide_drive.txt")
        os.remove("unhide_drive.txt")

        if result == 0:
            print(f"{letter}: USB sürücüsü başarıyla geri bağlandı.")
            hidden = load_hidden_volumes()
            if letter in hidden:
                hidden.remove(letter)
                save_hidden_volumes(hidden)
            #log_event("baris", "verified", "usb_unlocked", letter)
            return

    print(f"{letter}: USB sürücüsü bulunamadı.")

def process_disks(user_verified):
    allowed_disks = load_allowed_disks()
    partitions = psutil.disk_partitions()
    hidden = load_hidden_volumes()

    if user_verified:
        for letter in hidden:
            unhide_drive_windows(letter)
        return

    for part in partitions:
        disk = part.device
        letter = disk[0].upper()
        if disk not in allowed_disks:
            hide_drive_windows(letter)

