from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    """Schema for creating a notification (internal use)."""

    user_id: UUID
    type: str = Field(..., pattern="^(info|success|warning|error)$")
    title: str = Field(..., min_length=1, max_length=255)
    message: Optional[str] = None
    link: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Schema for notification response to client."""

    id: UUID
    type: str
    title: str
    message: Optional[str]
    link: Optional[str]
    is_read: bool
    extra_data: Optional[Dict[str, Any]]
    created_at: datetime
    read_at: Optional[datetime]

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Paginated notification list."""

    notifications: List[NotificationResponse]
    unread_count: int
    total: int


class MarkReadRequest(BaseModel):
    """Request to mark notifications as read."""

    notification_ids: List[UUID]


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    event: str  # new_notification, notification_read, notification_count
    data: Dict[str, Any]
