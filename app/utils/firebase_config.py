# lifelink-ai/backend/app/utils/firebase_config.py
import os
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase app once. Expects FIREBASE_CREDENTIALS env var pointing to JSON key file.
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "./firebase-key.json")

firebase_app = None

def init_firebase():
    global firebase_app
    if firebase_app is not None:
        return firebase_app

    if not os.path.exists(FIREBASE_CREDENTIALS):
        raise FileNotFoundError(
            f"Firebase credentials not found at {FIREBASE_CREDENTIALS}. "
            "Set FIREBASE_CREDENTIALS env var to the service account JSON file path."
        )

    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_app = firebase_admin.initialize_app(cred)
    return firebase_app

# convenience wrapper to send message (sync functions from firebase-admin)
def send_message(message):
    """
    message: firebase_admin.messaging.Message instance
    returns: message id (string)
    """
    init_firebase()
    return messaging.send(message)
