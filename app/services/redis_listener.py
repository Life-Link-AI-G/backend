# lifelink-ai/backend/app/services/redis_listener.py
import asyncio
import json
import logging
import os
import redis.asyncio as redis
from app.services.notification_service import send_to_token_async, send_to_topic_async
from app.core.config import settings

logger = logging.getLogger(__name__)

REDIS_CHANNEL = os.getenv("NOTIFICATION_CHANNEL", "notifications")

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def handle_message(data: dict):
    """
    Expected message schema (flexible):
    {
      "type": "token" | "topic",
      "token": "<fcm_token>",         # for type==token
      "topic": "user-123",            # for type==topic
      "title": "Alert!",
      "body": "High heart rate detected",
      "data": {...}                   # optional data payload
    }
    """
    t = data.get("type", "token")
    title = data.get("title", "LifeLink Alert")
    body = data.get("body", "")
    payload = data.get("data", {})

    try:
        if t == "token" and data.get("token"):
            return await send_to_token_async(data["token"], title, body, payload)
        elif t == "topic" and data.get("topic"):
            return await send_to_topic_async(data["topic"], title, body, payload)
        else:
            logger.warning("Invalid notification message: %s", data)
    except Exception as e:
        logger.exception("Failed to handle notification message: %s", e)

async def listen_for_notifications():
    """
    Long-running task to subscribe to the 'notifications' Redis channel.
    Call this from app startup event or run as a separate worker process.
    """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)
    logger.info("Subscribed to Redis channel: %s", REDIS_CHANNEL)

    while True:
        try:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                raw = message.get("data")
                if isinstance(raw, str):
                    try:
                        data = json.loads(raw)
                    except Exception:
                        logger.exception("Invalid JSON in notification message: %s", raw)
                        continue
                    asyncio.create_task(handle_message(data))
            await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logger.info("Notification listener cancelled")
            break
        except Exception as e:
            logger.exception("Error in notification listener: %s", e)
            await asyncio.sleep(1)
