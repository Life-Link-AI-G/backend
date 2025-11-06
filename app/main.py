# main_server.py
import sys
import os
import json
import asyncio
import random
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI

# --- FIX FOR IMPORT PATH ---
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- END FIX ---

# --- IMPORTS FOR AGENTS AND SCHEMAS ---
from app.auth import router as auth
from app.user_schema import RiskAnalysisRequest
from app.agents.mimic_human import UserProfile, RealTimeWearableData, Activity, get_instant_health_snapshot
from app.database import db

app = FastAPI(title="LifeLink AI - Main Server")

# -------------------------------
# Gemini Agent Integration
# -------------------------------
# Get API key from environment variables
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCiF_VKTJ2t5TT2JczRHilpoioCQaBChgI") # From gem_agent.py

def create_gemini_agent(sample: str, api_key: str) -> str:
    """
    Call the Gemini LLM to get a cardiac arrest risk score between 0 and 1.
    (Function copied from ai_services/agents/gem_agent.py)
    """
    template = f"""
You are an expert Health Analyst.
Based on the following user health data provide the risk score of cardiac arrest on a scale of 0-1 where 0 means no risk and 1 means high risk.
Return a JSON with two keys: "risk" and "short_report".
"risk" must be a float number between 0 and 1.
"short_report" must be a brief (2-3 sentences) explanation of the risk assessment.

User Health Data:
{sample}
"""
    try:
        # Ensure you have the correct model name and API key setup
        llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-2.5-flash", temperature=0)
        response = llm.invoke(template)
        return response.content
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Return a default error JSON
        return json.dumps({"risk": 0.0, "short_report": f"Error in analysis: {e}"})

def parse_gemini_response(response_json: str) -> Dict:
    """
    Parses the raw Gemini response, cleaning markdown code blocks.
    (Function based on logic in ai_services/agents/gem_agent.py)
    """
    try:
        # Clean markdown ```json ... ```
        start = response_json.find('```json')
        if start != -1:
            response_json = response_json[start+7:]
            end = response_json.find('```')
            if end != -1:
                response_json = response_json[:end]
        
        data = json.loads(response_json.strip())
        return data
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return {"risk": 0.0, "short_report": "Error parsing analysis."}

# -------------------------------
# Data structures
# -------------------------------
user_generators: Dict[str, RealTimeWearableData] = {}  # user_id -> data generator
user_activities: Dict[str, str] = {}                   # user_id -> current activity
MAX_USERS = 5
emergency_contacts: Dict[str, List[str]] = {}  # user_id -> [phone/email]
connected_frontends: Dict[str, WebSocket] = {}  # user_id -> websocket
app.include_router(auth, prefix="/api/auth", tags=["Authentication"])

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
# Initialize mimic users from Firebase
# -------------------------------
def init_users():
    profiles = get_users_from_db()
    for profile in profiles:
        user_generators[profile.user_id] = RealTimeWearableData(profile)
        user_activities[profile.user_id] = Activity.RESTING.value
    print(f"✅ Initialized {len(profiles)} users from Firebase.")

# -------------------------------
# Background task to generate and process data
# -------------------------------
async def generate_and_process_data():
    while True:
        if not user_generators:
            await asyncio.sleep(1)
            continue

        for user_id, generator in user_generators.items():
            activity = user_activities.get(user_id, random.choice(list(Activity)).value)
            data = generator.generate_realtime_data(activity)
            
            # Get physiological metrics for basic alert
            hr = data.get('physiological_metrics', {}).get('heart_rate', 0)
            stress = data.get('physiological_metrics', {}).get('stress_level', 0)
            
            print(f"[MIMIC DATA] {user_id}: HR={hr}, Stress={stress}")

            # --- Call Gemini Agent for Risk Analysis ---
            health_data_str = json.dumps(data)
            gemini_response_str = create_gemini_agent(health_data_str, GEMINI_API_KEY)
            gemini_data = parse_gemini_response(gemini_response_str)
            
            risk_score = gemini_data.get("risk", 0.0)
            risk_report = gemini_data.get("short_report", "")
            
            print(f"[GEMINI ANALYSIS] {user_id}: Risk={risk_score}, Report='{risk_report}'")

            # --- Alert Logic ---
            RISK_THRESHOLD = 0.7 
            alert_triggered = False
            alert_message = ""

            if hr > 120 or stress > 7:
                alert_triggered = True
                alert_message = f"Emergency! High Vitals: HR={hr}, Stress={stress}"
            elif risk_score > RISK_THRESHOLD:
                alert_triggered = True
                alert_message = f"AI EMERGENCY! High Cardiac Risk: {risk_score*100:.0f}%. Report: {risk_report}"

            # Send alert to frontend if triggered
            if alert_triggered and user_id in connected_frontends:
                frontend_ws = connected_frontends[user_id]
                await frontend_ws.send_text(json.dumps({
                    "alert": alert_message,
                    "hr": hr,
                    "stress": stress,
                    "ai_risk": risk_score,
                    "ai_report": risk_report
                }))
        await asyncio.sleep(1)

# -------------------------------
# Startup event
# -------------------------------
@app.on_event("startup")
async def startup_event():
    init_users()
    asyncio.create_task(generate_and_process_data())

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
# --- NEW: HTTP Endpoint for On-Demand Analysis ---
# -------------------------------
@app.post("/api/analyze_risk")
async def analyze_risk(request: RiskAnalysisRequest):
    """
    Receives user profile data, generates an instant health snapshot,
    and returns a Gemini risk analysis.
    """
    try:
        # 1. Create a UserProfile from the request
        user_profile = UserProfile(
            user_id=request.user_id,
            age=request.age,
            gender=request.gender,
            weight_kg=request.weight_kg,
            height_cm=request.height_cm,
            fitness_level=request.fitness_level
        )
        
        # 2. Generate the health snapshot
        snapshot_json_str = get_instant_health_snapshot(
            user_profile, 
            request.current_activity
        )
        
        # 3. Call Gemini Agent
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set on server")
        
        gemini_response_str = create_gemini_agent(snapshot_json_str, GEMINI_API_KEY)
        
        # 4. Parse and return the response
        gemini_data = parse_gemini_response(gemini_response_str)
        
        return {
            "analysis_input": json.loads(snapshot_json_str),
            "analysis_output": gemini_data
        }
    except ValueError as e:
        # This can happen if the activity string is invalid
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


# -------------------------------
# HTTP endpoint to add emergency contacts
# -------------------------------
@app.post("/add_contact/{user_id}")
async def add_contact(user_id: str, contact: str):
    if user_id not in emergency_contacts:
        emergency_contacts[user_id] = []
    emergency_contacts[user_id].append(contact)
    return {"status": f"Contact added for {user_id}", "contacts": emergency_contacts[user_id]}
