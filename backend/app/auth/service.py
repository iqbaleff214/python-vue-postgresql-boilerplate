import re
from typing import Optional

import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
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


def verify_google_token(credential: str) -> dict:
    """Verify a Google ID token and return its payload.

    Raises ValueError if the token is invalid or cannot be verified.
    """
    try:
        id_info = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError as e:
        raise ValueError(f"Invalid Google token: {e}")
    return id_info


async def verify_facebook_token(access_token: str) -> dict:
    """Verify a Facebook access token and return the user's profile dict.

    Raises ValueError if the token is invalid or the app ID does not match.
    """
    app_token = f"{settings.facebook_app_id}|{settings.facebook_app_secret}"
    async with httpx.AsyncClient() as client:
        debug_resp = await client.get(
            "https://graph.facebook.com/debug_token",
            params={"input_token": access_token, "access_token": app_token},
        )
        debug_resp.raise_for_status()
        debug_data = debug_resp.json().get("data", {})
        if not debug_data.get("is_valid"):
            raise ValueError("Invalid Facebook access token")
        if debug_data.get("app_id") != settings.facebook_app_id:
            raise ValueError("Facebook token app ID mismatch")

        profile_resp = await client.get(
            "https://graph.facebook.com/me",
            params={
                "fields": "id,name,first_name,last_name,email,picture.type(large)",
                "access_token": access_token,
            },
        )
        profile_resp.raise_for_status()
        return profile_resp.json()


async def _find_social_user(
    db: AsyncSession,
    *,
    social_field: str,
    social_id: str,
    email: str,
) -> User:
    """Find an existing user by social provider ID or email. Never creates accounts.

    Lookup order:
    1. Match by social_field stored in extra_data (fast path for already-linked accounts).
    2. Fall back to email match — auto-links the social ID for future logins.
    3. Raise ValueError if no matching account exists.
    """
    # 1. Try by social ID stored in extra_data
    result = await db.execute(
        select(User).where(User.extra_data[social_field].as_string() == social_id)
    )
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    # 2. Fall back to email match
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError(
            "No account found for this social login. Contact your administrator."
        )

    # Auto-link: store the social ID so future logins skip the email lookup
    extra = dict(user.extra_data or {})
    extra[social_field] = social_id
    user.extra_data = extra
    await db.commit()
    await db.refresh(user)
    return user


async def _create_social_user(
    db: AsyncSession,
    *,
    email: str,
    name: str,
    surname: Optional[str],
    avatar_url: Optional[str],
    google_id: Optional[str] = None,
    facebook_id: Optional[str] = None,
) -> User:
    """Create a new user account for a social login.

    The account is created with an unusable password and the social ID must be linked
    separately after creation.
    """
    user = User(
        name=name,
        surname=surname,
        email=email,
        phone_number=None,
        avatar_url=avatar_url,
        password_hash="",
        extra_data={
            "facebook_id": facebook_id,
            "google_id": google_id,
        },
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _find_or_create_social_user(
    db: AsyncSession,
    *,
    email: str,
    name: str,
    surname: Optional[str],
    avatar_url: Optional[str],
) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            name=name,
            surname=surname,
            email=email,
            phone_number=None,
            avatar_url=avatar_url,
            password_hash="",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def google_auth_user(db: AsyncSession, credential: str, is_signup: bool = False) -> User:
    id_info = verify_google_token(credential)

    email = id_info.get("email")
    if not email:
        raise ValueError("Google account has no email address")

    google_id = id_info.get("sub")
    if not google_id:
        raise ValueError("Google token missing user ID")
    
    if not is_signup:
        return await _find_social_user(
            db, social_field="google_id", social_id=google_id, email=email
        )
    
    # Ensure this Google ID is not already linked to a different account
    result = await db.execute(select(User).where(User.extra_data["google_id"].as_string() == google_id))
    existing: Optional[User] = result.scalar_one_or_none()
    if existing:
        raise ValueError("This Google account is already linked to another user.")
    
    return await _find_or_create_social_user(
        db,
        email=email,
        name=id_info.get("given_name") or id_info.get("name", "Unknown"),
        surname=id_info.get("family_name"),
        avatar_url=id_info.get("picture"),
        google_id=google_id,
    )


async def facebook_auth_user(db: AsyncSession, access_token: str, is_signup: bool = False) -> User:
    profile = await verify_facebook_token(access_token)

    email = profile.get("email")
    if not email:
        raise ValueError("Facebook account has no verified email address")

    facebook_id = profile.get("id")
    if not facebook_id:
        raise ValueError("Facebook token missing user ID")

    if not is_signup:
        return await _find_social_user(
            db, social_field="facebook_id", social_id=facebook_id, email=email
        )
    
    # Ensure this Facebook ID is not already linked to a different account
    result = await db.execute(select(User).where(User.extra_data["facebook_id"].as_string() == facebook_id))
    existing: Optional[User] = result.scalar_one_or_none()
    if existing:
        raise ValueError("This Facebook account is already linked to another user.")
    
    return await _create_social_user(
        db,
        email=email,
        name=profile.get("first_name") or profile.get("name", "Unknown"),
        surname=profile.get("last_name", None),
        avatar_url=profile.get("picture", {}).get("data", {}).get("url") or profile.get("picture"),
        facebook_id=facebook_id,
    )


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
