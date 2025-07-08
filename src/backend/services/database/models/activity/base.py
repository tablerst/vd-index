from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, TypeDecorator, String
import json


class UnicodePreservingJSON(TypeDecorator):
    """自定义JSON类型，确保中文字符不被转义为Unicode码"""
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """序列化时保持中文字符原样"""
        if value is not None:
            # 使用ensure_ascii=False确保中文字符不被转义
            return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
        return value

    def process_result_value(self, value, dialect):
        """反序列化时正常解析JSON"""
        if value is not None:
            # 如果已经是Python对象（list/dict），直接返回
            if isinstance(value, (list, dict)):
                return value
            # 如果是字符串，则解析JSON
            elif isinstance(value, str):
                return json.loads(value)
        return value


class Activity(SQLModel, table=True):
    """活动表模型"""
    __tablename__ = "activities"
    __table_args__ = {'extend_existing': True}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100, index=True)
    description: str = Field(max_length=500)
    date: datetime
    tags: List[str] = Field(sa_type=UnicodePreservingJSON, default_factory=list)

    # 参与成员 ID 列表（JSON 数组）
    participant_ids: List[int] = Field(
        sa_type=UnicodePreservingJSON, default_factory=list, description="Member.id 列表"
    )

    # 冗余统计字段，由业务侧在新增/更新时同步
    participants_total: int = Field(default=0, description="冗余成员总数")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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
