import firebase_admin
from firebase_admin import credentials, messaging
from typing import Dict

cred = credentials.Certificate("app/core/firebase_key.json")
firebase_admin.initialize_app(cred)

def send_push_notification(token: str, title: str, body: str, data: Dict = None):
    """
    Sends a push notification via Firebase Cloud Messaging.
    :param token: Device FCM token from frontend/mobile app
    :param title: Notification title
    :param body: Notification message body
    :param data: Optional custom payload
    """
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data or {}
    )

    try:
        response = messaging.send(message)
        print("✅ Notification sent successfully:", response)
        return response
    except Exception as e:
        print("❌ Failed to send notification:", str(e))
        return None
