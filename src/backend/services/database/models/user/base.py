"""
用户数据模型
系统登录用户表
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """系统用户模型"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 用户名（唯一）
    username: str = Field(max_length=50, unique=True, index=True)
    
    # 密码哈希（使用bcrypt）
    password_hash: str = Field(max_length=255)
    
    # 用户状态
    is_active: bool = Field(default=True)
    
    # 用户角色
    role: str = Field(default="admin", max_length=20)  # admin, editor, viewer
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 最后登录时间
    last_login: Optional[datetime] = None


class UserCreate(SQLModel):
    """创建用户的数据模型"""
    username: str = Field(max_length=50)
    password: str = Field(min_length=6, max_length=100)
    role: str = Field(default="admin", max_length=20)
    is_active: bool = Field(default=True)


class UserRead(SQLModel):
    """读取用户的数据模型"""
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class UserUpdate(SQLModel):
    """更新用户的数据模型"""
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    last_login: Optional[datetime] = None


class UserLogin(SQLModel):
    """用户登录数据模型"""
    username: str
    password: str
