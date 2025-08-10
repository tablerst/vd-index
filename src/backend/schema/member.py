"""
成员相关API数据模型
中文注释：原 member_schemas.py 重命名为 member.py，去除冗余后缀。
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MemberResponse(BaseModel):
    """成员信息响应模型（对外安全）"""
    id: int = Field(description="代理ID（安全的公开标识符）")
    name: str = Field(description="显示名称")
    avatar_url: str = Field(description="头像URL")
    bio: Optional[str] = Field(default=None, description="简介")
    join_date: str = Field(description="入群日期")
    role: int = Field(description="群权限：0=群主, 1=管理员, 2=群员")
    group_nick: Optional[str] = Field(default=None, description="群昵称")
    qq_nick: Optional[str] = Field(default=None, description="QQ昵称")


class MemberListResponse(BaseModel):
    """成员列表响应模型"""
    members: List[MemberResponse]
    total: int = Field(description="总成员数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total_pages: int = Field(description="总页数")


class MemberDetailResponse(MemberResponse):
    """成员详情响应模型"""
    level_point: Optional[int] = Field(default=None, description="群等级积分")
    level_value: Optional[int] = Field(default=None, description="群等级")
    q_age: Optional[int] = Field(default=None, description="Q龄")
    last_speak_time: Optional[str] = Field(default=None, description="最后发言时间")


class ImportMemberRequest(BaseModel):
    """导入成员请求模型"""
    uin: int = Field(description="QQ号")
    role: int = Field(description="群权限")
    join_time: int = Field(description="入群时间戳")
    last_speak_time: Optional[int] = Field(default=None, description="最后发言时间戳")
    card: str = Field(description="群昵称")
    nick: str = Field(description="QQ昵称")
    lv: dict = Field(description="等级信息")
    qage: Optional[int] = Field(default=None, description="Q龄")


class CreateMemberRequest(BaseModel):
    """手动创建成员请求模型"""
    display_name: str = Field(description="显示名称")
    group_nick: Optional[str] = Field(default=None, description="群昵称")
    role: int = Field(default=2, description="群权限：0=群主, 1=管理员, 2=群员")
    bio: Optional[str] = Field(default=None, description="简介/备注")


class ImportBatchRequest(BaseModel):
    """批量导入请求模型"""
    members: List[ImportMemberRequest] = Field(description="成员列表")


class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    data: Optional[dict] = Field(default=None, description="响应数据")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(description="错误类型")
    message: str = Field(description="错误消息")
    detail: Optional[str] = Field(default=None, description="错误详情")

