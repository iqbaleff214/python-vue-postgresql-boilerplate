"""Seed script to create an admin user."""

import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.database import async_session
from app.models.user import User


ADMIN_USER = {
    "name": "Admin",
    "surname": "User",
    "email": "admin@example.com",
    "phone_number": "+628000000000",
    "role": "ADMIN",
    "password": "password",
}


async def seed():
    async with async_session() as db:
        result = await db.execute(
            select(User).where(User.email == ADMIN_USER["email"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Admin user already exists: {existing.email} (role={existing.role})")
            return

        user = User(
            name=ADMIN_USER["name"],
            surname=ADMIN_USER["surname"],
            email=ADMIN_USER["email"],
            phone_number=ADMIN_USER["phone_number"],
            role=ADMIN_USER["role"],
            password_hash=hash_password(ADMIN_USER["password"]),
        )
        db.add(user)
        await db.commit()
        print(f"Admin user created: {user.email} / {ADMIN_USER['password']}")


if __name__ == "__main__":
    asyncio.run(seed())
