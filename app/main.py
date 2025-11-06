# main_server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from app.auth import router as auth
app = FastAPI(title="LifeLink AI - Main Server")

# -------------------------------
# Store emergency contacts per user
# -------------------------------
emergency_contacts: Dict[str, List[str]] = {}  # user_id -> [phone/email]
connected_frontends: Dict[str, WebSocket] = {}  # user_id -> websocket
app.include_router(auth, prefix="/api/auth", tags=["Authentication"])

# -------------------------------
# WebSocket endpoint to receive mimic data
# -------------------------------
@app.websocket("/ws/mimic_receive")
async def mimic_receive(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            payload = json.loads(msg)
            user_id = payload["user_id"]
            data = payload["data"]
            print(f"[MIMIC DATA] {user_id}: HR={data['physiological_metrics']['heart_rate']}, Stress={data['physiological_metrics']['stress_level']}")

            # If HR or stress triggers alert, send to frontend
            if user_id in connected_frontends:
                frontend_ws = connected_frontends[user_id]
                if data['physiological_metrics']['heart_rate'] > 120 or data['physiological_metrics']['stress_level'] > 7:
                    await frontend_ws.send_text(json.dumps({"alert": f"Emergency! HR={data['physiological_metrics']['heart_rate']}, Stress={data['physiological_metrics']['stress_level']}"}))
    except WebSocketDisconnect:
        print("Mimic connection disconnected")

# -------------------------------
# Frontend WS for streaming data & alerts
# -------------------------------
@app.websocket("/ws/frontend/{user_id}")
async def frontend_ws(user_id: str, ws: WebSocket):
    await ws.accept()
    connected_frontends[user_id] = ws
    try:
        while True:
            await asyncio.sleep(1)  # keep connection alive
    except WebSocketDisconnect:
        connected_frontends.pop(user_id, None)

# -------------------------------
# HTTP endpoint to add emergency contacts
# -------------------------------
@app.post("/add_contact/{user_id}")
async def add_contact(user_id: str, contact: str):
    if user_id not in emergency_contacts:
        emergency_contacts[user_id] = []
    emergency_contacts[user_id].append(contact)
    return {"status": f"Contact added for {user_id}", "contacts": emergency_contacts[user_id]}
