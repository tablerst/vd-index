"""
评论数据模型
匿名评论系统的核心数据结构
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Comment(SQLModel, table=True):
    """评论模型"""
    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}
    
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
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


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
