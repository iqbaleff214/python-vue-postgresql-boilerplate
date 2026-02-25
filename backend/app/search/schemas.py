from typing import Optional
from pydantic import BaseModel


class SearchItem(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    # Named icon key: "user" | "users" | "document" | "home" | "logout" | "sun" | "moon" | "monitor"
    icon: Optional[str] = None
    # Frontend route to navigate to when this item is selected
    url: Optional[str] = None


class SearchGroup(BaseModel):
    category: str
    items: list[SearchItem]


class SearchResponse(BaseModel):
    query: str
    groups: list[SearchGroup]
