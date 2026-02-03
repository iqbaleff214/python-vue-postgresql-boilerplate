import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.notifications import service
from app.notifications.schemas import (
    MarkReadRequest,
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
)
from app.notifications.broadcast import publish_notification
from app.notifications.websocket import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class SendNotificationRequest(BaseModel):
    """Request body for sending a notification."""

    user_email: Optional[str] = None
    user_id: Optional[UUID] = None
    type: str = Field("info", pattern="^(info|success|warning|error)$")
    title: str = Field(..., min_length=1, max_length=255)
    message: Optional[str] = None
    link: Optional[str] = None


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a notification to a user (admin only). Broadcasts via WebSocket if connected."""
    # Only admins can send notifications
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can send notifications")

    # Get target user
    if request.user_id:
        target_user_id = request.user_id
    elif request.user_email:
        result = await db.execute(
            select(User).where(User.email == request.user_email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        target_user_id = user.id
    else:
        raise HTTPException(
            status_code=400, detail="Either user_id or user_email must be provided"
        )

    # Create notification
    notification = await service.create_notification(
        db,
        NotificationCreate(
            user_id=target_user_id,
            type=request.type,
            title=request.title,
            message=request.message,
            link=request.link,
        ),
    )

    # Broadcast via Redis pub/sub (will be picked up by WebSocket handler)
    notification_data = NotificationResponse.model_validate(notification).model_dump(
        mode="json"
    )
    await publish_notification(target_user_id, "new_notification", notification_data)
    logger.info(f"Published notification to Redis for user {target_user_id}")

    return notification


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paginated list of notifications for the current user."""
    notifications = await service.get_user_notifications(
        db, current_user.id, limit=limit, offset=offset, unread_only=unread_only
    )
    unread_count = await service.get_unread_count(db, current_user.id)
    total = await service.get_total_count(db, current_user.id)

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        unread_count=unread_count,
        total=total,
    )


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get just the unread notification count."""
    count = await service.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.post("/mark-read")
async def mark_notifications_read(
    request: MarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark specific notifications as read."""
    updated = await service.mark_as_read(db, current_user.id, request.notification_ids)
    unread_count = await service.get_unread_count(db, current_user.id)

    # Notify other tabs/devices about the read status change
    await connection_manager.send_to_user(
        current_user.id, "notification_count", {"unread_count": unread_count}
    )

    return {"updated": updated, "unread_count": unread_count}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    updated = await service.mark_all_as_read(db, current_user.id)

    # Notify other tabs/devices
    await connection_manager.send_to_user(
        current_user.id, "notification_count", {"unread_count": 0}
    )

    return {"updated": updated, "unread_count": 0}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications.

    Connect with: ws://localhost:8001/notifications/ws?token=<jwt_token>
    """
    # Get token from query params
    token = websocket.query_params.get("token")
    if not token:
        logger.warning("WebSocket connection attempt without token")
        await websocket.close(code=4001, reason="Missing token")
        return

    # Validate token
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("WebSocket connection attempt with invalid token")
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id_str = payload.get("sub")
    if not user_id_str:
        logger.warning("WebSocket token missing subject (user ID)")
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        logger.warning("WebSocket token has invalid user ID format")
        await websocket.close(code=4001, reason="Invalid user ID")
        return

    logger.info(f"WebSocket connection attempt for user {user_id}")
    await connection_manager.connect(websocket, user_id)

    try:
        # Send initial unread count
        from app.database import async_session

        async with async_session() as db:
            unread_count = await service.get_unread_count(db, user_id)

        await websocket.send_json(
            {"event": "connected", "data": {"unread_count": unread_count}}
        )
        logger.info(f"WebSocket fully connected for user {user_id}")

        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong for connection keep-alive
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
        connection_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        connection_manager.disconnect(websocket, user_id)
