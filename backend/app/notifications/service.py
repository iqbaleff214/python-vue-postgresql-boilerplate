from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.notifications.schemas import NotificationCreate


async def create_notification(
    db: AsyncSession, data: NotificationCreate
) -> Notification:
    """Create a new notification and return it."""
    notification = Notification(
        user_id=data.user_id,
        type=data.type,
        title=data.title,
        message=data.message,
        link=data.link,
        extra_data=data.extra_data,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_user_notifications(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
) -> List[Notification]:
    """Get notifications for a user, ordered by created_at desc."""
    stmt = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)  # noqa: E712
    stmt = stmt.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
    """Get count of unread notifications for a user."""
    stmt = (
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def get_total_count(db: AsyncSession, user_id: UUID) -> int:
    """Get total count of notifications for a user."""
    stmt = (
        select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def mark_as_read(
    db: AsyncSession, user_id: UUID, notification_ids: List[UUID]
) -> int:
    """Mark specific notifications as read. Returns count of updated rows."""
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.id.in_(notification_ids),
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def mark_all_as_read(db: AsyncSession, user_id: UUID) -> int:
    """Mark all notifications as read for a user."""
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def get_notification(
    db: AsyncSession, notification_id: UUID, user_id: UUID
) -> Optional[Notification]:
    """Get a single notification by ID, ensuring it belongs to the user."""
    stmt = select(Notification).where(
        Notification.id == notification_id, Notification.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
