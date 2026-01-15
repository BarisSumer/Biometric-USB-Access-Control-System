import json
import os
from datetime import datetime

LOG_FILE = "log.json"

def log_event(user, status, action, disk):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "status": status,
        "action": action,
        "disk": disk
    }

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

    print(f"🔏 Loglandı: {log_entry}")
