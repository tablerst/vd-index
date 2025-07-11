"""
评论API响应模式定义
"""
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CommentResponse(BaseModel):
    """评论信息响应模型"""
    model_config = ConfigDict(
        # 确保datetime字段序列化为ISO格式并包含时区信息
        json_encoders={
            datetime: lambda v: (
                v.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
                if v and v.tzinfo is None
                else v.isoformat().replace('+00:00', 'Z')
            ) if v else None
        }
    )

    id: int = Field(description="评论ID")
    member_id: int = Field(description="关联的成员ID")
    content: str = Field(description="评论内容")
    likes: int = Field(description="点赞数")
    dislikes: int = Field(description="点踩数")
    is_anonymous: bool = Field(description="是否匿名")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class CommentCreateRequest(BaseModel):
    """创建评论请求模型"""
    content: str = Field(min_length=1, max_length=500, description="评论内容")
    is_anonymous: bool = Field(default=True, description="是否匿名")


class CommentListResponse(BaseModel):
    """评论列表响应模型"""
    comments: List[CommentResponse] = Field(description="评论列表")
    total: int = Field(description="总评论数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total_pages: int = Field(description="总页数")


class CommentStatsResponse(BaseModel):
    """评论统计响应模型"""
    total_comments: int = Field(description="总评论数")
    total_likes: int = Field(description="总点赞数")
    total_dislikes: int = Field(description="总点踩数")
    active_comments: int = Field(description="活跃评论数")
    deleted_comments: int = Field(description="已删除评论数")


class CommentActionResponse(BaseModel):
    """评论操作响应模型（点赞/点踩/删除）"""
    success: bool = Field(description="操作是否成功")
    message: str = Field(description="操作结果消息")
    comment: Optional[CommentResponse] = Field(default=None, description="更新后的评论信息")


class CommentModerationResponse(BaseModel):
    """评论管理响应模型"""
    high_dislike_comments: List[CommentResponse] = Field(description="高点踩评论列表")
    total: int = Field(description="符合条件的评论总数")
    threshold: int = Field(description="点踩数阈值")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(description="错误类型")
    message: str = Field(description="错误消息")
    detail: Optional[str] = Field(default=None, description="详细错误信息")
