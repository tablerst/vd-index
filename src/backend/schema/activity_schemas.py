"""
活动相关的API数据模型
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ParticipantInfo(BaseModel):
    """参与者信息"""
    id: int = Field(description="成员ID")
    name: str = Field(description="成员显示名称")
    avatar_url: str = Field(description="头像URL")


class ActivityResponse(BaseModel):
    """活动响应模型"""
    id: int = Field(description="活动ID")
    title: str = Field(description="活动标题")
    description: str = Field(description="活动描述")
    date: datetime = Field(description="活动日期")
    tags: List[str] = Field(description="活动标签")
    participants: List[ParticipantInfo] = Field(description="参与者列表")
    participants_total: int = Field(description="参与者总数")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ActivityListResponse(BaseModel):
    """活动列表响应模型"""
    activities: List[ActivityResponse] = Field(description="活动列表")
    total: int = Field(description="活动总数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total_pages: int = Field(description="总页数")


class ActivityStatsResponse(BaseModel):
    """活动统计响应模型"""
    total_activities: int = Field(description="活动总数")
    total_participants: int = Field(description="总参与人次")
    unique_participants: int = Field(description="独立参与成员数")


class ActivityCreateRequest(BaseModel):
    """创建活动请求模型"""
    title: str = Field(max_length=100, description="活动标题")
    description: str = Field(max_length=500, description="活动描述")
    date: datetime = Field(description="活动日期")
    tags: List[str] = Field(default_factory=list, description="活动标签")
    participant_ids: List[int] = Field(default_factory=list, description="参与成员ID列表")


class ActivityUpdateRequest(BaseModel):
    """更新活动请求模型"""
    title: Optional[str] = Field(None, max_length=100, description="活动标题")
    description: Optional[str] = Field(None, max_length=500, description="活动描述")
    date: Optional[datetime] = Field(None, description="活动日期")
    tags: Optional[List[str]] = Field(None, description="活动标签")
    participant_ids: Optional[List[int]] = Field(None, description="参与成员ID列表")


class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(description="操作是否成功")
    message: str = Field(description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")
