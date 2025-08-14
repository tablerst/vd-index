from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import ConfigDict, field_validator, model_validator

from ..base import now_naive, to_naive_beijing

class DailyPost(SQLModel, table=True):
    """Daily posts table model."""
    __tablename__ = "daily_posts"
    __table_args__ = {"extend_existing": True}
    model_config = ConfigDict(validate_assignment=True)

    id: Optional[int] = Field(default=None, primary_key=True)

    # Author user id (FK -> users.id)
    author_user_id: int = Field(foreign_key="users.id", index=True)

    # Main rich content JSONB (Tiptap full JSON)
    content_jsonb: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSONB)

    # Derived summary text (first paragraph plain text)
    content: Optional[str] = Field(default=None, max_length=2000)

    # Images and tags as JSON arrays (images[0] should mirror first image from content_jsonb when available)
    images: List[str] = Field(sa_type=JSONB, default_factory=list)
    tags: List[str] = Field(sa_type=JSONB, default_factory=list)

    # Counters
    likes_count: int = Field(default=0)
    comments_count: int = Field(default=0)
    views_count: int = Field(default=0, index=True)

    # Visibility
    published: bool = Field(default=True)

    # Timestamps (naive Beijing time, TIMESTAMP WITHOUT TIME ZONE)
    created_at: datetime = Field(default_factory=now_naive)
    updated_at: datetime = Field(default_factory=now_naive)

    @model_validator(mode="before")
    @classmethod
    def _coerce_time_fields(cls, data):
        if isinstance(data, dict):
            for key in ("created_at", "updated_at"):
                v = data.get(key)
                if isinstance(v, str):
                    try:
                        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except Exception as e:
                        raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                    data[key] = to_naive_beijing(dt)
        return data

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        for key in ("created_at", "updated_at"):
            v = getattr(self, key, None)
            if isinstance(v, str):
                try:
                    dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                except Exception as e:
                    raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                setattr(self, key, to_naive_beijing(dt))

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _v_ts(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return to_naive_beijing(v)


class DailyPostCreate(SQLModel):
    """Payload to create a DailyPost.
    Backward compatible: either provide content_jsonb (preferred) or legacy content/images.
    """
    content_jsonb: Optional[Dict[str, Any]] = None
    content: Optional[str] = Field(default=None, max_length=2000)
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    published: bool = Field(default=True)


class DailyPostRead(SQLModel):
    """Read model for DailyPost."""
    id: int
    author_user_id: int
    content_jsonb: Optional[Dict[str, Any]] = None
    content: Optional[str]
    images: List[str]
    tags: List[str]
    likes_count: int
    comments_count: int
    views_count: int
    published: bool
    created_at: datetime
    updated_at: datetime


class DailyPostUpdate(SQLModel):
    """Patch-update model for DailyPost.
    Backward compatible: allow updating content_jsonb or legacy fields.
    """
    content_jsonb: Optional[Dict[str, Any]] = None
    content: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    published: Optional[bool] = None
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None
    # views_count is managed by service (increment), not arbitrary set

