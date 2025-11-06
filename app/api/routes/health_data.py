# app/api/routes/health_data.py
from fastapi import APIRouter
from app.api.schemas.health_schema import HealthData
from app.services.redis_service import publish_event

router = APIRouter()

@router.post("/update")
async def update_health(data: HealthData):
    # Send vitals data to Redis channel for AI to pick up
    await publish_event("vitals:raw", data.model_dump())
    return {"status": "queued", "user_id": data.user_id}
