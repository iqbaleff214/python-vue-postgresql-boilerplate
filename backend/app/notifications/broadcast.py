"""
Redis-based notification broadcasting.

This module provides functions to broadcast notifications via Redis pub/sub,
allowing notifications to be sent from any process (CLI, Celery, API) and
received by the WebSocket connections in the running server.
"""

import json
import logging
from typing import Any, Dict
from uuid import UUID

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

NOTIFICATION_CHANNEL = "notifications:broadcast"


def get_redis_client() -> redis.Redis:
    """Get a Redis client instance."""
    return redis.from_url(settings.redis_url, decode_responses=True)


async def publish_notification(user_id: UUID, event: str, data: Dict[str, Any]) -> None:
    """
    Publish a notification to Redis for broadcasting via WebSocket.

    This can be called from any process (CLI, Celery, API endpoint).
    The running server's WebSocket handler will pick it up and send to connected clients.
    """
    client = get_redis_client()
    try:
        message = json.dumps({
            "user_id": str(user_id),
            "event": event,
            "data": data,
        })
        await client.publish(NOTIFICATION_CHANNEL, message)
        logger.info(f"Published notification to Redis: {event} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to publish notification to Redis: {e}")
    finally:
        await client.aclose()


async def subscribe_to_notifications(callback):
    """
    Subscribe to the notification channel and call the callback for each message.

    This should be run as a background task in the FastAPI server.
    """
    client = get_redis_client()
    pubsub = client.pubsub()

    try:
        await pubsub.subscribe(NOTIFICATION_CHANNEL)
        logger.info(f"Subscribed to Redis channel: {NOTIFICATION_CHANNEL}")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    user_id = UUID(data["user_id"])
                    event = data["event"]
                    notification_data = data["data"]
                    await callback(user_id, event, notification_data)
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")
    except Exception as e:
        logger.error(f"Redis subscription error: {e}")
    finally:
        await pubsub.unsubscribe(NOTIFICATION_CHANNEL)
        await client.aclose()
