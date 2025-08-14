"""
评论数据模型
匿名评论系统的核心数据结构
"""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict, field_serializer, field_validator, model_validator

from ..base import now_naive, to_naive_beijing


class Comment(SQLModel, table=True):
    """评论模型"""
    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}
    model_config = ConfigDict(validate_assignment=True)
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 关联的成员ID（外键）
    member_id: int = Field(foreign_key="members.id", index=True)
    
    # 评论内容
    content: str = Field(max_length=500, description="评论内容，最大500字符")
    
    # 点赞数
    likes: int = Field(default=0, description="点赞数量")
    
    # 点踩数
    dislikes: int = Field(default=0, description="点踩数量")
    
    # 是否匿名（默认为True）
    is_anonymous: bool = Field(default=True, description="是否匿名评论")
    
    # 作者IP地址（用于防刷和管理）
    author_ip: Optional[str] = Field(default=None, max_length=45, description="评论者IP地址")
    
    # 软删除标记
    is_deleted: bool = Field(default=False, description="是否已删除")
    
    # 时间戳 - 存储“无时区北京时间”（数据库字段为TIMESTAMP WITHOUT TIME ZONE）
    created_at: datetime = Field(default_factory=now_naive, description="创建时间")
    updated_at: datetime = Field(default_factory=now_naive, description="更新时间")

    @model_validator(mode="before")
    @classmethod
    def _coerce_time_fields(cls, data):
        """统一将字符串形式的时间字段解析并转换为无时区北京时间。"""
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
        """在模型初始化完成后进行兜底时间字段规范化。"""
        for key in ("created_at", "updated_at"):
            v = getattr(self, key, None)
            if isinstance(v, str):
                try:
                    dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                except Exception as e:
                    raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                setattr(self, key, to_naive_beijing(dt))


class CommentCreate(SQLModel):
    """创建评论的数据模型"""
    member_id: int = Field(description="关联的成员ID")
    content: str = Field(min_length=1, max_length=500, description="评论内容")
    is_anonymous: bool = Field(default=True, description="是否匿名")
    author_ip: Optional[str] = Field(default=None, max_length=45, description="作者IP")


class CommentRead(SQLModel):
    """读取评论的数据模型"""
    id: int
    member_id: int
    content: str
    likes: int
    dislikes: int
    is_anonymous: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """将UTC时间序列化为ISO格式字符串（带时区信息）"""
        if dt.tzinfo is None:
            # 如果没有时区信息，假设是UTC时间
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class CommentUpdate(SQLModel):
    """更新评论的数据模型"""
    content: Optional[str] = Field(default=None, min_length=1, max_length=500)
    likes: Optional[int] = Field(default=None, ge=0)
    dislikes: Optional[int] = Field(default=None, ge=0)
    is_deleted: Optional[bool] = Field(default=None)


class CommentStats(SQLModel):
    """评论统计数据模型"""
    total_comments: int = Field(description="总评论数")
    total_likes: int = Field(description="总点赞数")
    total_dislikes: int = Field(description="总点踩数")
    active_comments: int = Field(description="活跃评论数（未删除）")
    deleted_comments: int = Field(description="已删除评论数")
