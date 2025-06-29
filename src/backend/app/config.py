"""
应用配置模块
"""
import os
import secrets
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import json


class Settings(BaseSettings):
    """应用设置"""
    
    # 数据库配置
    database_url: str = "sqlite:///./data/members.db"
    
    # 头像文件存储
    avatar_root: str = "./data/avatars"
    
    # 加密配置
    uin_aes_key: str = ""
    secret_key_file: str = "./secret_key"
    
    # JWT配置
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS配置
    allowed_origins: List[str] = Field(
        default=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:3000",  # 其他开发服务器
            "https://tomo-loop.icu"   # 生产域名
        ],
        env="ALLOWED_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "tomo-loop.icu"],
        env="ALLOWED_HOSTS"
    )
    
    # 速率限制
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        json_loads = json.loads


def get_settings() -> Settings:
    """获取应用设置"""
    return Settings()


def ensure_secret_key() -> str:
    """确保密钥文件存在，如果不存在则生成"""
    settings = get_settings()
    secret_file = Path(settings.secret_key_file)
    
    if secret_file.exists():
        return secret_file.read_text().strip()
    
    # 生成新的密钥
    secret_key = secrets.token_urlsafe(32)
    
    # 确保目录存在
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入密钥文件
    secret_file.write_text(secret_key)
    
    # 设置文件权限（仅所有者可读写）
    secret_file.chmod(0o600)
    
    return secret_key


def get_or_create_aes_key() -> str:
    """获取或创建AES加密密钥"""
    settings = get_settings()
    
    # 优先使用环境变量
    if settings.uin_aes_key:
        return settings.uin_aes_key
    
    # 否则使用密钥文件
    return ensure_secret_key()


# 全局设置实例
settings = get_settings()
