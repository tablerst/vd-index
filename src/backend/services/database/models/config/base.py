"""
配置数据模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict, field_validator, model_validator

from ..base import now_naive, to_naive_beijing


class Config(SQLModel, table=True):
    """配置表"""
    __tablename__ = "config"
    __table_args__ = {'extend_existing': True}
    model_config = ConfigDict(validate_assignment=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(max_length=100, unique=True, index=True)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    type: str = Field(default="string", max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=now_naive)
    updated_at: datetime = Field(default_factory=now_naive)

    @model_validator(mode="before")
    @classmethod
    def _coerce_time_fields(cls, data):
        if isinstance(data, dict):
            for key in ("created_at", "updated_at"):
                v = data.get(key)
                if isinstance(v, str):
                    try:
                        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except Exception as e:
                        raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                    data[key] = to_naive_beijing(dt)
        return data

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        for key in ("created_at", "updated_at"):
            v = getattr(self, key, None)
            if isinstance(v, str):
                try:
                    dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                except Exception as e:
                    raise ValueError(f"Invalid datetime string for {key}: {v}") from e
                setattr(self, key, to_naive_beijing(dt))

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _v_ts(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return to_naive_beijing(v)


class ConfigCreate(SQLModel):
    """创建配置的数据模型"""
    key: str = Field(max_length=100)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    type: str = Field(default="string", max_length=20)
    is_active: bool = Field(default=True)


class ConfigRead(SQLModel):
    """读取配置的数据模型"""
    id: int
    key: str
    value: str
    description: Optional[str] = None
    type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ConfigUpdate(SQLModel):
    """更新配置的数据模型"""
    value: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
