from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

class Activity(SQLModel, table=True):
    """活动表模型"""
    __tablename__ = "activities"
    __table_args__ = {'extend_existing': True}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100, index=True)
    description: str = Field(max_length=500)
    date: datetime
    tags: List[str] = Field(sa_type=JSONB, default_factory=list)

    # 参与成员 ID 列表（JSON 数组）
    participant_ids: List[int] = Field(
        sa_type=JSONB, default_factory=list, description="Member.id 列表"
    )

    # 冗余统计字段，由业务侧在新增/更新时同步
    participants_total: int = Field(default=0, description="冗余成员总数")

    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class ActivityCreate(SQLModel):
    """创建活动的数据模型"""
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    date: datetime
    tags: List[str] = Field(default_factory=list)
    participant_ids: List[int] = Field(default_factory=list)


class ActivityRead(SQLModel):
    """读取活动的数据模型"""
    id: int
    title: str
    description: str
    date: datetime
    tags: List[str]
    participant_ids: List[int]
    participants_total: int
    created_at: datetime
    updated_at: datetime


class ActivityUpdate(SQLModel):
    """更新活动的数据模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    participant_ids: Optional[List[int]] = None
