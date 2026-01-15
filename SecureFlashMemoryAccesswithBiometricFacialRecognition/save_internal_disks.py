import json
import psutil
import platform

def get_internal_disks():
    internal_disks = []

    for part in psutil.disk_partitions(all=False):
        if "cdrom" in part.opts or part.fstype == '':
            continue

        # Windows için local diskleri filtrele
        if platform.system() == "Windows":
            device = part.device
            if not device.startswith("\\\\"):  # ağ sürücülerini alma
                internal_disks.append(device)

    return internal_disks

def save_disks_to_file(disk_list, file_name="allowed_disks.json"):
    with open(file_name, "w") as f:
        json.dump(disk_list, f, indent=4)
    print(f"{file_name} dosyasına kaydedildi.")

if __name__ == "__main__":
    disks = get_internal_disks()
    print("Bulunan Dahili Diskler:")
    for d in disks:
        print("-", d)
    save_disks_to_file(disks)
