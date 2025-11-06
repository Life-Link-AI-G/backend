# app/api/routes/alerts.py
from fastapi import APIRouter
from app.api.schemas.alert_schema import Alert
from app.services.notification_service import send_alert

router = APIRouter()

@router.post("/trigger")
async def trigger_alert(alert: Alert):
    ok = await send_alert(alert)
    return {"status": "sent" if ok else "failed"}