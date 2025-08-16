"""
每日帖评论数据模型（DailyPostComment）
- 仅登录用户可评论（绑定 author_user_id -> users.id）
- 与具体 DailyPost 绑定（post_id -> daily_posts.id）
- 支持可选的父子评论（parent_id 自引用）
- 计数与软删除字段，与项目时间规范保持一致（naive 北京时间）
"""
from datetime import datetime, timezone
from typing import Optional

from pydantic import ConfigDict, field_serializer, field_validator
from sqlmodel import SQLModel, Field

from ..base import now_naive, to_naive_beijing


class DailyPostComment(SQLModel, table=True):
    """每日帖评论模型"""
    __tablename__ = "daily_post_comments"
    __table_args__ = {"extend_existing": True}
    model_config = ConfigDict(validate_assignment=True)

    # PK
    id: Optional[int] = Field(default=None, primary_key=True)

    # 外键
    post_id: int = Field(foreign_key="daily_posts.id", index=True, description="关联的 DailyPost ID")
    author_user_id: int = Field(foreign_key="users.id", index=True, description="评论作者的用户ID")

    # 父评论（可选，自引用实现楼中楼）
    parent_id: Optional[int] = Field(
        default=None,
        foreign_key="daily_post_comments.id",
        index=True,
        description="父评论ID（用于回复）",
    )

    # 评论内容
    content: str = Field(max_length=1000, description="评论内容，最大1000字符")

    # 互动计数
    likes: int = Field(default=0, description="点赞数量")
    dislikes: int = Field(default=0, description="点踩数量")

    # 管理/状态
    author_ip: Optional[str] = Field(default=None, max_length=45, description="评论者IP地址")
    is_deleted: bool = Field(default=False, description="软删除标记")

    # 时间戳（存储无时区北京时间，TIMESTAMP WITHOUT TIME ZONE）
    created_at: datetime = Field(default_factory=now_naive, description="创建时间")
    updated_at: datetime = Field(default_factory=now_naive, description="更新时间")

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _coerce_time(cls, v):
        """将传入的字符串/aware datetime 统一为无时区北京时间。"""
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return to_naive_beijing(v)


class DailyPostCommentCreate(SQLModel):
    """创建评论的数据模型
    - 登录上下文中获取 author_user_id
    - 必须提供 post_id 和 content
    - 可选 parent_id 以支持回复
    """
    post_id: int
    content: str = Field(min_length=1, max_length=1000)
    parent_id: Optional[int] = Field(default=None)
    author_ip: Optional[str] = Field(default=None, max_length=45)


class DailyPostCommentRead(SQLModel):
    """读取评论的数据模型"""
    id: int
    post_id: int
    author_user_id: int
    parent_id: Optional[int]
    content: str
    likes: int
    dislikes: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        """将无时区时间序列化为ISO字符串（补齐时区为UTC以兼容前端）"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class DailyPostCommentUpdate(SQLModel):
    """更新评论的数据模型"""
    content: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    likes: Optional[int] = Field(default=None, ge=0)
    dislikes: Optional[int] = Field(default=None, ge=0)
    is_deleted: Optional[bool] = Field(default=None)

