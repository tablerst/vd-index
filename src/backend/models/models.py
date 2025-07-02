"""
数据模型定义
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session
from core.config import settings


class Member(SQLModel, table=True):
    """群成员模型"""
    __tablename__ = "members"
    
    # 主键：代理ID（对外公开的安全ID）
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 显示名称（群昵称优先，否则QQ昵称）
    display_name: str = Field(max_length=100, index=True)
    
    # 群昵称
    group_nick: Optional[str] = Field(default=None, max_length=100)
    
    # QQ昵称
    qq_nick: Optional[str] = Field(default=None, max_length=100)
    
    # 加密的UIN（AES-256-GCM加密）
    uin_encrypted: str = Field(max_length=500)
    
    # 混淆用随机salt (16字节hex)
    salt: str = Field(max_length=32)
    
    # 头像文件哈希（用于生成安全的头像URL）
    avatar_hash: str = Field(max_length=64, index=True)
    
    # 群权限：0=群主, 1=管理员, 2=群员
    role: int = Field(default=2)
    
    # 入群时间
    join_time: datetime
    
    # 最后发言时间
    last_speak_time: Optional[datetime] = None
    
    # 群等级信息
    level_point: Optional[int] = Field(default=0)
    level_value: Optional[int] = Field(default=1)
    
    # Q龄
    q_age: Optional[int] = Field(default=0)
    
    # 创建时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 更新时间
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Config(SQLModel, table=True):
    """配置表"""
    __tablename__ = "config"
    
    key: str = Field(primary_key=True, max_length=100)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)



