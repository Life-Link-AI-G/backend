# main_server/notifier.py
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client
from config import settings

# -------------------------------
# Firebase setup
# -------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_service_account.json")  # your Firebase service account
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -------------------------------
# Twilio setup
# -------------------------------
client = None
if settings.TWILIO_SID and settings.TWILIO_AUTH:
    client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH)

# -------------------------------
# Helper to get emergency contacts
# -------------------------------
def get_emergency_contacts(user_id: str):
    """Fetch emergency contacts for a user from Firebase."""
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("emergency_contacts", [])  # expect a list of phone numbers
    return []

# -------------------------------
# Send SMS alert
# -------------------------------
def send_sms_alert(user_id: str, message: str):
    contacts = get_emergency_contacts(user_id)
    if not client:
        print(f"🚫 Twilio not configured, skipping SMS for {user_id}")
        return
    if not contacts:
        print(f"⚠️ No emergency contacts for {user_id}")
        return
    for contact in contacts:
        msg = client.messages.create(
            body=f"[LifeLink AI] ALERT for {user_id}: {message}",
            from_=settings.TWILIO_PHONE,
            to=contact
        )
        print(f"📱 SMS sent to {contact}: {msg.sid}")

# -------------------------------
# Make emergency call
# -------------------------------
def make_emergency_call(user_id: str, message: str):
    contacts = get_emergency_contacts(user_id)
    if not client:
        print(f"🚫 Twilio not configured, skipping call for {user_id}")
        return
    if not contacts:
        print(f"⚠️ No emergency contacts for {user_id}")
        return
    for contact in contacts:
        call = client.calls.create(
            twiml=f"<Response><Say voice='alice'>{message}</Say></Response>",
            from_=settings.TWILIO_PHONE,
            to=contact
        )
        print(f"📞 Call placed to {contact}: {call.sid}")
