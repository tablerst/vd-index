"""
配置管理相关的数据模式
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ConfigResponse(BaseModel):
    """配置响应模型"""
    id: int
    key: str
    value: str
    description: Optional[str] = None
    type: str = "string"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigListResponse(BaseModel):
    """配置列表响应模型"""
    configs: List[ConfigResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ConfigCreateRequest(BaseModel):
    """创建配置请求模型"""
    key: str = Field(..., min_length=1, max_length=100, description="配置键")
    value: str = Field(..., max_length=1000, description="配置值")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")
    type: str = Field("string", description="配置类型")
    is_active: bool = Field(True, description="是否启用")

    @validator('key')
    def validate_key(cls, v):
        """验证配置键格式"""
        if not v.replace('_', '').replace('.', '').replace('-', '').isalnum():
            raise ValueError('配置键只能包含字母、数字、下划线、点和连字符')
        return v

    @validator('type')
    def validate_type(cls, v):
        """验证配置类型"""
        allowed_types = ['string', 'number', 'boolean', 'json']
        if v not in allowed_types:
            raise ValueError(f'配置类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class ConfigUpdateRequest(BaseModel):
    """更新配置请求模型"""
    value: Optional[str] = Field(None, max_length=1000, description="配置值")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")
    type: Optional[str] = Field(None, description="配置类型")
    is_active: Optional[bool] = Field(None, description="是否启用")

    @validator('type')
    def validate_type(cls, v):
        """验证配置类型"""
        if v is not None:
            allowed_types = ['string', 'number', 'boolean', 'json']
            if v not in allowed_types:
                raise ValueError(f'配置类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None
