#!/usr/bin/env python
"""CLI script to send notifications to users.

Usage:
    python send_notification.py --user-id <uuid> --type info --title "Hello" --message "World"
    python send_notification.py --email iqbaleff214@gmail.com --type success --title "Task Complete"
    python send_notification.py --all --type warning --title "System Maintenance"
"""

import argparse
import asyncio
import sys
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select

from app.database import async_session
from app.models.notification import Notification  # noqa: F401 - needed for model registry
from app.models.user import User
from app.notifications.broadcast import publish_notification
from app.notifications.schemas import NotificationCreate, NotificationResponse
from app.notifications.service import create_notification


async def get_user_by_email(db, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_all_user_ids(db) -> List[UUID]:
    result = await db.execute(select(User.id))
    return [row[0] for row in result.fetchall()]


async def send_and_notify(
    user_id: UUID,
    notification_type: str,
    title: str,
    message: Optional[str],
    link: Optional[str],
) -> Notification:
    """Create notification in DB and broadcast via Redis pub/sub."""
    async with async_session() as db:
        notification = await create_notification(
            db,
            NotificationCreate(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                link=link,
            ),
        )

        # Broadcast via Redis (will be picked up by running server's WebSocket handler)
        notification_data = NotificationResponse.model_validate(notification).model_dump(
            mode="json"
        )
        await publish_notification(
            user_id,
            "new_notification",
            notification_data,
        )

        return notification


async def main():
    parser = argparse.ArgumentParser(description="Send notifications to users")

    # Target selection (mutually exclusive)
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--user-id", type=str, help="Target user UUID")
    target_group.add_argument("--email", type=str, help="Target user email")
    target_group.add_argument("--all", action="store_true", help="Send to all users")

    # Notification content
    parser.add_argument(
        "--type",
        choices=["info", "success", "warning", "error"],
        default="info",
        help="Notification type",
    )
    parser.add_argument("--title", required=True, help="Notification title")
    parser.add_argument("--message", help="Notification message body")
    parser.add_argument("--link", help="Optional action URL")

    args = parser.parse_args()

    async with async_session() as db:
        user_ids: list[UUID] = []

        if args.user_id:
            try:
                user_ids = [UUID(args.user_id)]
            except ValueError:
                print(f"Error: Invalid UUID: {args.user_id}", file=sys.stderr)
                sys.exit(1)
        elif args.email:
            user = await get_user_by_email(db, args.email)
            if not user:
                print(f"Error: User not found with email: {args.email}", file=sys.stderr)
                sys.exit(1)
            user_ids = [user.id]
        else:  # --all
            user_ids = await get_all_user_ids(db)
            if not user_ids:
                print("Error: No users found in database", file=sys.stderr)
                sys.exit(1)

    print(f"Sending notification to {len(user_ids)} user(s)...")

    for user_id in user_ids:
        notification = await send_and_notify(
            user_id=user_id,
            notification_type=args.type,
            title=args.title,
            message=args.message,
            link=args.link,
        )
        print(f"  Created: {notification.id} for user {user_id}")

    print(f"Done! Sent {len(user_ids)} notification(s).")


if __name__ == "__main__":
    asyncio.run(main())
