# 🔐 Biometric USB Access Control System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Security](https://img.shields.io/badge/Security-AES%20Encryption-green)
![AI](https://img.shields.io/badge/AI-DeepFace%20%7C%20OpenCV-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

**Biometric USB Access Control** is a cybersecurity software designed to secure data on removable storage devices. Unlike traditional password protection, this system uses **Face Recognition** to authorize access. 

[cite_start]When a USB drive is inserted, the system automatically detects it, **locks the drive** (hides the volume) immediately, and only restores access if the user is verified via the webcam[cite: 1242, 1263].

## 🛡️ Key Features

* [cite_start]**Auto-Lock Mechanism:** Uses Windows `diskpart` commands to instantly remove the drive letter of any newly inserted USB device, rendering it inaccessible to the OS until verified[cite: 1271].
* [cite_start]**AI-Powered Authentication:** Utilizes **DeepFace** (FaceNet/Google) models to compare the live user against a local database of authorized personnel[cite: 1253].
* **AES-256 Encryption:** All biometric reference data (face images) stored on the disk are encrypted using `cryptography.fernet`. [cite_start]The data is decrypted only in RAM during verification[cite: 1280].
* [cite_start]**Intruder Capture:** If an unauthorized user attempts to access the drive, the system denies access and automatically saves a photo of the intruder to the `screenshots/` folder[cite: 1278].
* [cite_start]**Offline Security:** The system operates entirely locally (offline), ensuring no biometric data is sent to the cloud[cite: 1249].
* **Audit Logging:** detailed JSON logs track every event, including USB insertion, verification success/failure, and drive unlocking.

## 🏗️ System Architecture

The project is modularized for security and maintainability:

1.  **`main.py`:** The GUI and Orchestrator. It runs background threads to monitor hardware changes and manages the Tkinter interface.
2.  **`usb_control.py`:** Handles low-level OS interactions. It identifies removable drives and executes `diskpart` scripts to hide or unhide volumes.
3.  **`verify_user.py`:** The AI engine. It captures video frames, decrypts the local dataset on the fly, and performs facial verification.
4.  **`encryptor.py`:** Manages the generation of the `secret.key` and handles the encryption/decryption of user photos.
5.  **`logger.py`:** Records security events with timestamps.

## 🛠️ Installation & Requirements

### Prerequisites
* [cite_start]**OS:** Windows 10/11 (Required for `diskpart` and drive letter management)[cite: 1255].
* **Hardware:** Webcam.
* **Python:** 3.10 or higher.

### Dependencies
Install the required libraries:

```bash
pip install deepface opencv-python pillow psutil cryptography tf-keras

Note: Since this tool manipulates drive letters, you must run the script as Administrator.

🚀 Usage Guide
1. System Safety Setup
Before running the security system, you must whitelist your internal hard drives (C:, D:, etc.) to prevent accidental locking.

Bash

python save_internal_disks.py
This generates an allowed_disks.json file.

2. Launch the Application
Start the main security interface:

Bash

python main.py
3. Register a User
Click "Yeni Kullanıcı Ekle" (Add New User).

Enter a username.

Look at the camera and press SPACE to capture reference photos.

Press ESC to save. The images are automatically encrypted and stored in encrypted_faces/.

4. Operation
Keep the application running (it monitors in the background).

Insert a USB Drive.

The drive will disappear from File Explorer immediately.

A camera window will appear asking for verification.

If Verified: The drive letter is assigned, and the USB opens.

If Denied: The drive remains hidden, and an intruder alert is logged.

📂 Project Structure
Plaintext

├── main.py                  # Main Application Entry
├── usb_control.py           # Diskpart automation logic
├── verify_user.py           # DeepFace recognition logic
├── encryptor.py             # AES Security logic
├── logger.py                # Logging system
├── save_internal_disks.py   # Whitelisting tool
├── encrypted_faces/         # Encrypted biometric database (Local)
├── screenshots/             # Intruder evidence
└── secret.key               # AES Key (DO NOT SHARE)
⚠️ Disclaimer
This software interacts with Windows Partition Manager (diskpart). While safeguards are in place, use it responsibly. Always ensure your system drives are whitelisted using save_internal_disks.py before enabling the auto-lock feature.
