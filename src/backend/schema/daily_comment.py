"""
DailyPost 评论 API schema（与 /api/v1 路由对接）
"""
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DailyCommentItem(BaseModel):
    """单条评论（含基本字段+可选作者聚合信息）"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: (
                v.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
                if v and v.tzinfo is None
                else v.isoformat().replace('+00:00', 'Z')
            ) if v else None
        }
    )

    id: int
    post_id: int
    author_user_id: int
    # 可选：作者显示名与头像URL（服务端按需聚合，前端需容错）
    author_display_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    parent_id: Optional[int] = None
    content: str
    likes: int
    dislikes: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class DailyCommentListResponse(BaseModel):
    """顶层+子回复的列表响应"""
    top_comments: List[DailyCommentItem]
    children_map: dict[int, list[DailyCommentItem]] = Field(
        default_factory=dict,
        description="键为顶层评论ID，值为该评论的所有子回复数组"
    )
    total: int
    page: int
    page_size: int
    total_pages: int


class DailyCommentCreateRequest(BaseModel):
    """创建评论/回复的请求体"""
    content: str = Field(min_length=1, max_length=1000)
    parent_id: Optional[int] = Field(default=None)


class DailyCommentActionResponse(BaseModel):
    success: bool
    message: str
    comment: Optional[DailyCommentItem] = None

