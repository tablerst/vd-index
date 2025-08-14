"""
用户数据模型
系统登录用户表
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import field_validator, model_validator

from ..base import now_naive, to_naive_beijing


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

    # 绑定的成员ID（唯一，一对一绑定）
    member_id: Optional[int] = Field(default=None, foreign_key="members.id", unique=True, index=True)

    # 时间戳（无时区北京时间）
    created_at: datetime = Field(default_factory=now_naive)
    updated_at: datetime = Field(default_factory=now_naive)

    # 最后登录时间（无时区北京时间）
    last_login: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_time_fields(cls, data):
        if isinstance(data, dict):
            for key in ("created_at", "updated_at", "last_login"):
                v = data.get(key)
                if isinstance(v, str):
                    try:
                        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except Exception as e:
                        raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                    data[key] = to_naive_beijing(dt)
        return data

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        for key in ("created_at", "updated_at", "last_login"):
            v = getattr(self, key, None)
            if isinstance(v, str):
                try:
                    dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                except Exception as e:
                    raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                setattr(self, key, to_naive_beijing(dt))

    @field_validator("last_login", "created_at", "updated_at", mode="before")
    @classmethod
    def _v_ts(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return to_naive_beijing(v)


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
