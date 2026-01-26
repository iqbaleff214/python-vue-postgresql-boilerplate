import re

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import RegisterRequest, TokenResponse
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User


def is_email(identifier: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", identifier) is not None


async def authenticate_user(
    db: AsyncSession, identifier: str, password: str
) -> User | None:
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
