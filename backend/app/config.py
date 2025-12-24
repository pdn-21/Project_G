import os
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Create Key if not exists
KEY = os.getenv("ENCRYPTION_KEY")
if not KEY:
    KEY = Fernet.generate_key().decode()
    print(f"!!! GENERATED NEW KEY: {KEY} (SAVE TO .env) !!!")

cipher_suite = Fernet(KEY.encode())
CONFIG_FILE = "config.enc"

def save_config(data: dict):
    # Load existing to merge
    current = load_config()
    current.update(data)
    encrypted_data = cipher_suite.encrypt(json.dumps(current).encode())
    with open(CONFIG_FILE, "wb") as f:
        f.write(encrypted_data)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
        return json.loads(decrypted_data)
    except Exception:
        return {}