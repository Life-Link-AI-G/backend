# main_server/notifier.py
import os
from twilio.rest import Client
from main_server.config import settings

client = None
if settings.TWILIO_SID and settings.TWILIO_AUTH:
    client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH)

# Sample emergency contacts per user
EMERGENCY_CONTACTS = {
    "USER_100": ["+919999999999"],
    "USER_101": ["+918888888888"]
}

def send_sms_alert(user_id: str, message: str):
    if not client:
        print(f"🚫 Twilio not configured, skipping SMS for {user_id}")
        return
    for contact in EMERGENCY_CONTACTS.get(user_id, []):
        msg = client.messages.create(
            body=f"[LifeLink AI] ALERT for {user_id}: {message}",
            from_=settings.TWILIO_PHONE,
            to=contact
        )
        print(f"📱 SMS sent to {contact}: {msg.sid}")

def make_emergency_call(user_id: str, message: str):
    if not client:
        print(f"🚫 Twilio not configured, skipping call for {user_id}")
        return
    for contact in EMERGENCY_CONTACTS.get(user_id, []):
        call = client.calls.create(
            twiml=f"<Response><Say voice='alice'>{message}</Say></Response>",
            from_=settings.TWILIO_PHONE,
            to=contact
        )
        print(f"📞 Call placed to {contact}: {call.sid}")
