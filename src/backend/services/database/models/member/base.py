"""
群成员数据模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict, field_validator, model_validator

from ..base import now_naive, to_naive_beijing


class Member(SQLModel, table=True):
    """群成员模型"""
    __tablename__ = "members"
    __table_args__ = {'extend_existing': True}
    model_config = ConfigDict(validate_assignment=True)
    
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
    
    # 创建时间（无时区北京时间）
    created_at: datetime = Field(default_factory=now_naive)

    # 更新时间（无时区北京时间）
    updated_at: datetime = Field(default_factory=now_naive)

    @model_validator(mode="before")
    @classmethod
    def _coerce_time_fields(cls, data):
        if isinstance(data, dict):
            for key in ("join_time", "last_speak_time", "created_at", "updated_at"):
                v = data.get(key)
                if isinstance(v, str):
                    try:
                        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except Exception as e:
                        raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                    data[key] = to_naive_beijing(dt)
        return data

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        for key in ("join_time", "last_speak_time", "created_at", "updated_at"):
            v = getattr(self, key, None)
            if isinstance(v, str):
                try:
                    dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                except Exception as e:
                    raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                setattr(self, key, to_naive_beijing(dt))

    @field_validator("join_time", "last_speak_time", "created_at", "updated_at", mode="before")
    @classmethod
    def _v_ts(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return to_naive_beijing(v)


class MemberCreate(SQLModel):
    """创建成员的数据模型"""
    display_name: str = Field(max_length=100)
    group_nick: Optional[str] = Field(default=None, max_length=100)
    qq_nick: Optional[str] = Field(default=None, max_length=100)
    uin_encrypted: str = Field(max_length=500)
    salt: str = Field(max_length=32)
    role: int = Field(default=2)
    join_time: datetime
    last_speak_time: Optional[datetime] = None
    level_point: Optional[int] = Field(default=0)
    level_value: Optional[int] = Field(default=1)
    q_age: Optional[int] = Field(default=0)


class MemberRead(SQLModel):
    """读取成员的数据模型"""
    id: int
    display_name: str
    group_nick: Optional[str] = None
    qq_nick: Optional[str] = None
    role: int
    join_time: datetime
    last_speak_time: Optional[datetime] = None
    level_point: Optional[int] = None
    level_value: Optional[int] = None
    q_age: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class MemberUpdate(SQLModel):
    """更新成员的数据模型"""
    display_name: Optional[str] = None
    group_nick: Optional[str] = None
    qq_nick: Optional[str] = None
    role: Optional[int] = None
    last_speak_time: Optional[datetime] = None
    level_point: Optional[int] = None
    level_value: Optional[int] = None
    q_age: Optional[int] = None
