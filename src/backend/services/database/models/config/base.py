"""
配置数据模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Config(SQLModel, table=True):
    """配置表"""
    __tablename__ = "config"
    __table_args__ = {'extend_existing': True}
    
    key: str = Field(primary_key=True, max_length=100)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConfigCreate(SQLModel):
    """创建配置的数据模型"""
    key: str = Field(max_length=100)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)


class ConfigRead(SQLModel):
    """读取配置的数据模型"""
    key: str
    value: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ConfigUpdate(SQLModel):
    """更新配置的数据模型"""
    value: Optional[str] = None
    description: Optional[str] = None
