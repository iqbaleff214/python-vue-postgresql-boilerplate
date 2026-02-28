import os
import uuid as uuid_mod

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import verify_facebook_token, verify_google_token
from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.users.schemas import (
    ChangePasswordRequest,
    ConnectFacebookRequest,
    ConnectGoogleRequest,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.phone_number and data.phone_number != current_user.phone_number:
        existing = await db.execute(
            select(User).where(User.phone_number == data.phone_number)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use",
            )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be JPEG, PNG, WebP, or GIF",
        )

    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must not exceed 5 MB",
        )

    avatars_dir = os.path.join(settings.upload_dir, "avatars")
    os.makedirs(avatars_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "avatar.jpg")[1] or ".jpg"
    filename = f"{uuid_mod.uuid4().hex}{ext}"
    filepath = os.path.join(avatars_dir, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    # Remove old avatar file if it was a local upload
    if current_user.avatar_url and current_user.avatar_url.startswith("/uploads/"):
        old_path = current_user.avatar_url.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

    current_user.avatar_url = f"/uploads/avatars/{filename}"
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.put("/me/password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"detail": "Password changed successfully"}


@router.post("/me/connect/google", response_model=UserResponse)
async def connect_google(
    data: ConnectGoogleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        id_info = verify_google_token(data.credential)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    google_id = id_info.get("sub")
    if not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Google token missing user ID"
        )

    # Ensure this Google ID is not already linked to a different account
    result = await db.execute(
        select(User).where(User.extra_data["google_id"].as_string() == google_id)
    )
    existing = result.scalar_one_or_none()
    if existing and existing.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Google account is already linked to another user.",
        )

    extra = dict(current_user.extra_data or {})
    extra["google_id"] = google_id
    current_user.extra_data = extra
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me/connect/google", response_model=UserResponse)
async def disconnect_google(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    extra = dict(current_user.extra_data or {})
    extra.pop("google_id", None)
    current_user.extra_data = extra
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/me/connect/facebook", response_model=UserResponse)
async def connect_facebook(
    data: ConnectFacebookRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await verify_facebook_token(data.access_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    facebook_id = profile.get("id")
    if not facebook_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Facebook token missing user ID"
        )

    # Ensure this Facebook ID is not already linked to a different account
    result = await db.execute(
        select(User).where(User.extra_data["facebook_id"].as_string() == facebook_id)
    )
    existing = result.scalar_one_or_none()
    if existing and existing.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Facebook account is already linked to another user.",
        )

    extra = dict(current_user.extra_data or {})
    extra["facebook_id"] = facebook_id
    current_user.extra_data = extra
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me/connect/facebook", response_model=UserResponse)
async def disconnect_facebook(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    extra = dict(current_user.extra_data or {})
    extra.pop("facebook_id", None)
    current_user.extra_data = extra
    await db.commit()
    await db.refresh(current_user)
    return current_user

