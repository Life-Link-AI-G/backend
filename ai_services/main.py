# mimic_server.py
import asyncio
import json
import random
from typing import Dict, List
from fastapi import FastAPI
import websockets
import firebase_admin
from firebase_admin import credentials, firestore
from agents.mimic_human import UserProfile, RealTimeWearableData, Activity

# -------------------------------
# CONFIGURATION
# -------------------------------
MAIN_SERVER_WS = "ws://localhost:8000/ws/mimic_receive"  # main server WS
MAX_USERS = 5

app = FastAPI(title="Mimic Wearable Data Server")

# -------------------------------
# Firebase setup
# -------------------------------
cred = credentials.Certificate("firebase-key.json")  # put your Firebase service account JSON here
firebase_admin.initialize_app(cred)
db = firestore.client()

# -------------------------------
# Data structures
# -------------------------------
user_generators: Dict[str, RealTimeWearableData] = {}  # user_id -> data generator
user_activities: Dict[str, str] = {}                   # user_id -> current activity

# -------------------------------
# Fetch users from Firebase
# -------------------------------
def get_users_from_db(limit: int = MAX_USERS) -> List[UserProfile]:
    users_ref = db.collection("users").limit(limit).stream()
    profiles = []
    for doc in users_ref:
        data = doc.to_dict()
        profiles.append(UserProfile(
            user_id=data["user_id"],
            age=data.get("age", 30),
            gender=data.get("gender", "M"),
            weight_kg=data.get("weight_kg", 70),
            height_cm=data.get("height_cm", 170),
            fitness_level=data.get("fitness_level", "average")
        ))
    return profiles

# -------------------------------
# Mimic streaming logic
# -------------------------------
async def send_to_main_server():
    while True:
        if not user_generators:
            await asyncio.sleep(1)
            continue

        try:
            async with websockets.connect(MAIN_SERVER_WS) as ws:
                while True:
                    for user_id, generator in user_generators.items():
                        activity = user_activities.get(user_id, random.choice(list(Activity)).value)
                        data = generator.generate_realtime_data(activity)
                        payload = {"user_id": user_id, "data": data}
                        await ws.send(json.dumps(payload))
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"❌ Connection to main server lost: {e}")
            await asyncio.sleep(5)  # retry after delay

# -------------------------------
# Initialize mimic users from Firebase
# -------------------------------
def init_users():
    profiles = get_users_from_db()
    for profile in profiles:
        user_generators[profile.user_id] = RealTimeWearableData(profile)
        user_activities[profile.user_id] = Activity.RESTING.value
    print(f"✅ Initialized {len(profiles)} users from Firebase.")

# -------------------------------
# HTTP endpoints
# -------------------------------
@app.get("/")
async def root():
    return {"message": "Mimic server running, streaming data for Firebase users."}

@app.get("/active_users")
async def active_users():
    return {"users": list(user_generators.keys()), "total": len(user_generators)}

# -------------------------------
# Startup event
# -------------------------------
@app.on_event("startup")
async def startup_event():
    init_users()
    asyncio.create_task(send_to_main_server())

# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
