from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass
class Category:
    id: int
    name: str
    slug: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Tag:
    id: int
    name: str
    slug: str

@dataclass
class Post:
    id: int
    title: str
    content: str
    slug: str
    category_id: int
    category: Optional[Category] = None
    tag_ids: list[int] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    published: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

@dataclass
class Comment:
    id: int
    post_id: int
    author_name: str
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
