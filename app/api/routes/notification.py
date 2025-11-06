# lifelink-ai/backend/app/api/v1/notifications.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.services.notification_service import send_to_token_async, send_to_topic_async

router = APIRouter(prefix="/api/v1/notify", tags=["notifications"])
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.notification_service import send_push_notification

router = APIRouter()

class NotificationRequest(BaseModel):
    token: str
    title: str
    body: str

@router.post("/send")
def send_notification(req: NotificationRequest):
    res = send_push_notification(req.token, req.title, req.body)
    if res:
        return {"success": True, "message_id": res}
    return {"success": False, "error": "Failed to send"}

class NotifyTokenRequest(BaseModel):
    token: str
    title: str
    body: str
    data: Optional[Dict[str, str]] = None

class NotifyTopicRequest(BaseModel):
    topic: str
    title: str
    body: str
    data: Optional[Dict[str, str]] = None

@router.post("/user")
async def notify_user(req: NotifyTokenRequest):
    try:
        message_id = await send_to_token_async(req.token, req.title, req.body, req.data)
        return {"status": "sent", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/topic")
async def notify_topic(req: NotifyTopicRequest):
    try:
        message_id = await send_to_topic_async(req.topic, req.title, req.body, req.data)
        return {"status": "sent", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
