import subprocess

def get_volume_number(letter):
    result = subprocess.run("echo list volume | diskpart", shell=True, capture_output=True, text=True)
    lines = result.stdout.splitlines()
    for line in lines:
        if f"{letter} " in line or f"{letter}:" in line:
            print(f"Diskpart çıktısı: {line}")
            parts = line.split()
            if len(parts) >= 2 and parts[0].lower().startswith("volume"):
                print(f"{letter} sürücüsü Volume numarası: {parts[1]}")
                return parts[1]
    print(f"{letter} için volume numarası bulunamadı.")
    return ""

drive_letter = input("Sürücü harfi girin (örnek: G): ").strip().upper()
get_volume_number(drive_letter)
