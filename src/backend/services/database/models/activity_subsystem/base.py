"""
SQLModel tables for the new Activities subsystem (vote/thread).

Note: We use table names prefixed with act_ to avoid conflicts with the
existing "activities" (star calendar) module.
"""
from __future__ import annotations

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT

from ..base import now_naive


class ActActivity(SQLModel, table=True):
    """Activity container for both vote and thread types."""

    __tablename__ = "act_activity"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(max_length=16, description="vote | thread")
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)
    anonymous_allowed: bool = Field(default=True)
    allow_change: bool = Field(default=True, description="Whether changing/revoking vote is allowed")
    starts_at: Optional[datetime] = Field(default=None)
    ends_at: Optional[datetime] = Field(default=None)
    status: str = Field(default="ongoing", max_length=16)  # draft/ongoing/closed
    created_at: datetime = Field(default_factory=now_naive)


class ActVoteOption(SQLModel, table=True):
    """Vote options for vote-type activities."""

    __tablename__ = "act_activity_vote_option"
    __table_args__ = (
        UniqueConstraint("activity_id", "label", name="uq_act_activity_option_label"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="act_activity.id")
    label: str = Field(max_length=200)
    member_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=now_naive)


class ActVoteRecord(SQLModel, table=True):
    """Single-choice vote records. One record per user per activity."""

    __tablename__ = "act_activity_vote_record"
    __table_args__ = (
        UniqueConstraint("activity_id", "voter_id", name="uq_act_activity_voter"),
        Index("ix_act_vote_record_activity", "activity_id"),
        Index("ix_act_vote_record_voter", "voter_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="act_activity.id")
    option_id: int = Field(foreign_key="act_activity_vote_option.id")
    voter_id: int = Field(default=0)
    display_anonymous: bool = Field(default=False)
    created_at: datetime = Field(default_factory=now_naive)


class ActThreadPost(SQLModel, table=True):
    """Posts for thread-type activities (simple flat list with optional parent_id)."""

    __tablename__ = "act_activity_thread_post"

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="act_activity.id")
    author_id: int = Field(default=0)
    display_anonymous: bool = Field(default=False)
    content: str = Field()
    parent_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=now_naive)


class ActAuditLog(SQLModel, table=True):
    """Minimal audit log for actions on activities."""

    __tablename__ = "act_activity_audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(default=0)
    actor_id: int = Field(default=0)
    action: str = Field(max_length=50)
    metadata_json: Optional[str] = Field(default=None, description="JSON string metadata")
    created_at: "datetime" = Field(default_factory=now_naive)

