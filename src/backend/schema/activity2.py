from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    """Request model to create a new activity (vote-only in v2)."""

    type: str = Field(pattern="^(vote)$", default="vote")
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    anonymous_allowed: bool = True
    allow_change: bool = True
    starts_at: Optional[str] = None  # ISO string, naive (Beijing time) per project convention
    ends_at: Optional[str] = None


class ActivityOut(BaseModel):
    id: int
    type: str
    title: str
    description: Optional[str] = None
    status: str
    anonymous_allowed: bool
    allow_change: bool
    starts_at: Optional[str] = None
    ends_at: Optional[str] = None
    creator_id: int


class VoteSubmit(BaseModel):
    option_id: int
    display_anonymous: bool = False


class ThreadPostCreate(BaseModel):
    content: str = Field(min_length=1)
    display_anonymous: bool = False
    parent_id: Optional[int] = None


class VoteOptionCreate(BaseModel):
    label: str = Field(min_length=1, max_length=200)
    member_id: Optional[int] = None


class VoteOptionOut(BaseModel):
    id: int
    label: str
    member_id: Optional[int] = None


class RankingEntry(BaseModel):
    option_id: int
    label: str
    votes: int


class RankingOut(BaseModel):
    entries: List[RankingEntry]


class ActivityListItem(BaseModel):
    id: int
    type: str
    title: str
    description: Optional[str] = None
    status: str
    creator_id: int


class ActivityListOut(BaseModel):
    items: List[ActivityListItem]
    total: int
    page: int
    size: int

