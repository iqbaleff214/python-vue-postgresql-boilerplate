import asyncio
import json
import logging
from typing import Dict, Optional, Set
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per user."""

    def __init__(self):
        # user_id -> set of WebSocket connections (supports multiple tabs/devices)
        self._connections: Dict[UUID, Set[WebSocket]] = {}
        self._redis_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, user_id: UUID) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        logger.info(
            f"WebSocket connected for user {user_id}. "
            f"Active connections: {len(self._connections[user_id])}"
        )

    def disconnect(self, websocket: WebSocket, user_id: UUID) -> None:
        """Remove a WebSocket connection."""
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_to_user(self, user_id: UUID, event: str, data: dict) -> None:
        """Send a message to all connections of a specific user (local only)."""
        if user_id not in self._connections:
            logger.info(f"No local connections found for user {user_id}")
            return

        message = json.dumps({"event": event, "data": data})
        dead_connections = set()
        connection_count = len(self._connections[user_id])
        logger.info(
            f"Sending '{event}' to {connection_count} connection(s) for user {user_id}"
        )

        for websocket in self._connections[user_id]:
            try:
                await websocket.send_text(message)
                logger.info(f"Message sent successfully to user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to send to websocket: {e}")
                dead_connections.add(websocket)

        # Clean up dead connections
        for ws in dead_connections:
            self._connections[user_id].discard(ws)

    def is_user_connected(self, user_id: UUID) -> bool:
        """Check if user has any active connections."""
        return user_id in self._connections and len(self._connections[user_id]) > 0

    def get_connection_count(self, user_id: UUID) -> int:
        """Get number of active connections for a user."""
        return len(self._connections.get(user_id, set()))

    async def start_redis_listener(self) -> None:
        """Start listening to Redis pub/sub for notifications."""
        from app.notifications.broadcast import subscribe_to_notifications

        async def handle_redis_message(user_id: UUID, event: str, data: dict):
            """Handle incoming Redis messages and forward to WebSocket."""
            logger.info(f"Received Redis message: {event} for user {user_id}")
            await self.send_to_user(user_id, event, data)

        self._redis_task = asyncio.create_task(
            subscribe_to_notifications(handle_redis_message)
        )
        logger.info("Started Redis pub/sub listener for notifications")

    async def stop_redis_listener(self) -> None:
        """Stop the Redis listener."""
        if self._redis_task:
            self._redis_task.cancel()
            try:
                await self._redis_task
            except asyncio.CancelledError:
                pass
            self._redis_task = None
            logger.info("Stopped Redis pub/sub listener")


# Singleton instance
connection_manager = ConnectionManager()
