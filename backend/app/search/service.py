"""
Search service with a pluggable provider registry.

To add a new searchable data source, define an async function matching
the SearchProvider signature and append it to PROVIDERS:

    async def search_orders(db, user, query, limit):
        if user.role not in ("ADMIN", "STAFF"):
            return []
        rows = await db.execute(select(Order).where(Order.ref.ilike(f"%{query}%")).limit(limit))
        return [SearchItem(id=str(o.id), label=o.ref, url=f"/orders/{o.id}") for o in rows.scalars()]

    PROVIDERS.append(("Orders", search_orders))
"""

from typing import Callable, Awaitable

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.search.schemas import SearchGroup, SearchItem

# Type alias for a search provider function
SearchProvider = Callable[
    [AsyncSession, User, str, int],
    Awaitable[list[SearchItem]],
]


async def _search_users(
    db: AsyncSession, current_user: User, query: str, limit: int
) -> list[SearchItem]:
    """Search users by name, surname, email, or phone. Admin-only."""
    if current_user.role != "ADMIN":
        return []

    pattern = f"%{query}%"
    stmt = (
        select(User)
        .where(
            or_(
                User.name.ilike(pattern),
                User.surname.ilike(pattern),
                User.email.ilike(pattern),
                User.phone_number.ilike(pattern),
            )
        )
        .limit(limit)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()

    return [
        SearchItem(
            id=str(u.id),
            label=f"{u.name} {u.surname or ''}".strip(),
            description=u.email,
            icon="user",
            url="/a/accounts",
        )
        for u in users
    ]


# ── Provider registry ─────────────────────────────────────────────────────────
# Each entry is (category_label, provider_function).
# Providers are called in order; empty results are silently omitted.
PROVIDERS: list[tuple[str, SearchProvider]] = [
    ("Users", _search_users),
    # Register additional providers here as the app grows.
]


async def run_search(
    db: AsyncSession,
    current_user: User,
    query: str,
    limit: int = 5,
) -> list[SearchGroup]:
    groups: list[SearchGroup] = []
    for category, provider in PROVIDERS:
        items = await provider(db, current_user, query, limit)
        if items:
            groups.append(SearchGroup(category=category, items=items))
    return groups
