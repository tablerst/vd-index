"""
Daily posts API schemas
中文注释：日常动态 API 的请求/响应模型，配合 /api/v1/daily 使用。
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_serializer


class DailyPostItem(BaseModel):
    """列表与详情使用的基础帖子结构。
    说明：author_display_name 与 author_avatar_url 为服务端可选聚合字段，
    当前实现阶段可返回 None，前端需做容错。
    """
    id: int
    author_user_id: int
    author_display_name: Optional[str] = Field(default=None, description="作者显示名（可选聚合字段）")
    author_avatar_url: Optional[str] = Field(default=None, description="作者头像URL（可选聚合字段）")
    content_jsonb: Optional[Dict[str, Any]] = Field(default=None, description="Tiptap完整JSON结构，用于富文本渲染")
    content: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    likes_count: int
    comments_count: int
    views_count: int
    published: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO string with UTC timezone if naive.
        中文注释：将UTC naive时间补齐为UTC时区并序列化为ISO字符串，确保前端收到字符串。
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class DailyPostListResponse(BaseModel):
    """分页列表响应"""
    posts: List[DailyPostItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class UploadImageItem(BaseModel):
    """上传后返回的单文件信息"""
    name: str
    url: str
    width: Optional[int] = None
    height: Optional[int] = None


class UploadImagesResponse(BaseModel):
    """批量上传响应"""
    files: List[UploadImageItem]


class CreateDailyRequest(BaseModel):
    """创建帖子请求（如不直接使用 SQLModel 的 Create 模型时备用）"""
    content_jsonb: Optional[Dict[str, Any]] = None
    content: Optional[str] = Field(default=None, max_length=2000)
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    published: bool = True


class UpdateDailyRequest(BaseModel):
    """更新帖子请求（备用）"""
    content_jsonb: Optional[Dict[str, Any]] = None
    content: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    published: Optional[bool] = None
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None

