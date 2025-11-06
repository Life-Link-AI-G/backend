# app/main.py
from fastapi import FastAPI
from app.api.routes import health_data, alerts, websocket

app = FastAPI(title="LifeLink AI Backend", version="1.0")

# include endpoints from each route file
app.include_router(health_data.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["WebSocket"])

@app.get("/")
def root():
    return {"status": "Backend running!"}
