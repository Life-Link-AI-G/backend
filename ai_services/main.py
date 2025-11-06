# mimic_server.py
import asyncio
import json
import random
from typing import Dict
from fastapi import FastAPI, WebSocket
import websockets
from mimic_human import UserProfile, RealTimeWearableData, Activity

app = FastAPI(title="Mimic Wearable Data Server")

# -------------------------------
# Data structures
# -------------------------------
user_generators: Dict[str, RealTimeWearableData] = {}  # user_id -> data generator
user_activities: Dict[str, str] = {}                   # user_id -> current activity
MAX_USERS = 5
MAIN_SERVER_WS = "ws://localhost:8000/ws/mimic_receive"  # main server WS

# -------------------------------
# Mimic streaming logic
# -------------------------------
async def send_to_main_server():
    while True:
        if not user_generators:
            await asyncio.sleep(1)
            continue
        async with websockets.connect(MAIN_SERVER_WS) as ws:
            while True:
                for user_id, generator in user_generators.items():
                    activity = user_activities.get(user_id, random.choice(list(Activity)).value)
                    data = generator.generate_realtime_data(activity)
                    payload = {"user_id": user_id, "data": data}
                    await ws.send(json.dumps(payload))
                await asyncio.sleep(1)

# -------------------------------
# WebSocket endpoint for main server
# -------------------------------
@app.websocket("/ws/start_mimic")
async def start_mimic(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            payload = json.loads(msg)
            user_id = payload["user_id"]
            profile_data = payload["profile"]

            if len(user_generators) >= MAX_USERS and user_id not in user_generators:
                await ws.send_text(json.dumps({"status": "max_users_reached", "user_id": user_id}))
                continue

            # Initialize or update user generator
            user_profile = UserProfile(**profile_data)
            user_generators[user_id] = RealTimeWearableData(user_profile)
            user_activities[user_id] = payload.get("activity", Activity.RESTING.value)

            await ws.send_text(json.dumps({"status": f"Mimic started for {user_id}"}))
    except Exception as e:
        print(f"WebSocket disconnected: {e}")

# -------------------------------
# HTTP endpoint to view active mimic users
# -------------------------------
@app.get("/active_users")
async def active_users():
    return {"users": list(user_generators.keys()), "total": len(user_generators)}

# -------------------------------
# HTTP endpoint to stop a user
# -------------------------------
@app.post("/stop_user/{user_id}")
async def stop_user(user_id: str):
    if user_id in user_generators:
        user_generators.pop(user_id)
        user_activities.pop(user_id, None)
        return {"status": f"{user_id} stopped"}
    return {"status": f"{user_id} not found"}

# -------------------------------
# Run mimic streaming loop in background
# -------------------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_to_main_server())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
