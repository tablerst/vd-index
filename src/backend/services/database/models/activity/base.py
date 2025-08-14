from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import field_validator, model_validator
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

from backend.services.database.models.base import now_naive, to_naive_beijing


class Activity(SQLModel, table=True):
    """活动表模型"""

    __tablename__ = "activities"
    __table_args__ = {"extend_existing": True}

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

    created_at: datetime = Field(default_factory=now_naive)
    updated_at: datetime = Field(default_factory=now_naive)
    def model_post_init(self, __context) -> None:  # type: ignore[override]
        """在模型初始化完成后进行兜底时间字段规范化。
        中文注释：处理仍为字符串的时间字段，统一转换为“无时区北京时间”。
        """
        for key in ("date", "created_at", "updated_at"):
            v = getattr(self, key, None)
            if isinstance(v, str):
                try:
                    dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                except Exception as e:
                    raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                setattr(self, key, to_naive_beijing(dt))


    @model_validator(mode="before")
    @classmethod
    def _coerce_time_fields(cls, data):
        """统一将字符串形式的时间字段解析并转换为无时区北京时间。
        中文注释：兜底处理，确保即使字段级校验器未触发，字符串时间也会被正确转换。
        """
        if isinstance(data, dict):
            for key in ("date", "created_at", "updated_at"):
                v = data.get(key)
                if isinstance(v, str):
                    # 允许 Z 结尾或带偏移量的 ISO 字符串
                    try:
                        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except Exception as e:
                        raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                    data[key] = to_naive_beijing(dt)
        return data

    @field_validator("date", mode="before")
    @classmethod
    def _v_date(cls, v):
        if isinstance(v, str):
            # 如果是字符串，尝试解析为 datetime 对象
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return to_naive_beijing(v)

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _v_ts(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            # 如果是字符串，尝试解析为 datetime 对象
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return to_naive_beijing(v)


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
