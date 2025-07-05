from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, JSON

class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100, index=True)
    description: str = Field(max_length=500)
    date: datetime
    tags: List[str] = Field(sa_type=JSON, default_factory=list)

    # 参与成员 ID 列表（JSON 数组）
    participant_ids: List[int] = Field(
        sa_type=JSON, default_factory=list, description="Member.id 列表"
    )

    # 冗余统计字段，由业务侧在新增/更新时同步
    participants_total: int = Field(default=0, description="冗余成员总数")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
