import re
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import RegisterRequest, TokenResponse
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_reset_token,
    decode_reset_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.tasks.email import send_reset_password_email


def is_email(identifier: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", identifier) is not None


async def authenticate_user(
    db: AsyncSession, identifier: str, password: str
) -> Optional[User]:
    if is_email(identifier):
        stmt = select(User).where(User.email == identifier)
    else:
        stmt = select(User).where(User.phone_number == identifier)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    result = await db.execute(
        select(User).where(
            or_(User.email == data.email, User.phone_number == data.phone_number)
        )
    )
    if result.scalar_one_or_none():
        raise ValueError("Email or phone number already registered")

    user = User(
        name=data.name,
        surname=data.surname,
        email=data.email,
        phone_number=data.phone_number,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def create_user_token(user: User) -> TokenResponse:
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


async def forgot_password(db: AsyncSession, email: str) -> None:
    """Look up user by email, generate reset token, enqueue email task.

    Always returns None (no error) to avoid leaking whether the email exists.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        return

    token = create_reset_token(str(user.id))
    reset_link = f"{settings.frontend_url}/reset-password?token={token}"

    send_reset_password_email.delay(
        to_email=user.email,
        user_name=user.name,
        reset_link=reset_link,
    )


async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    """Decode reset token and update the user's password.

    Raises ValueError if the token is invalid or expired, or user not found.
    """
    user_id = decode_reset_token(token)
    if user_id is None:
        raise ValueError("Invalid or expired reset token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError("Invalid or expired reset token")

    user.password_hash = hash_password(new_password)
    await db.commit()
