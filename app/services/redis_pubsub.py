# app/services/redis_pubsub.py
import redis.asyncio as redis
import json
from backend.api.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def publish_event(channel: str, data: dict):
    """Publish a message to a Redis channel."""
    await redis_client.publish(channel, json.dumps(data))

async def subscribe_to_channel(channel: str):
    """Subscribe to a Redis channel (for WebSocket updates)."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    return pubsub
