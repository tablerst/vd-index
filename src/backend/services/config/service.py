"""
配置服务模块
"""
import secrets
import logging
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

# 设置日志记录器
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """应用设置"""
    
    # 数据库配置
    database_url: str = "postgresql+asyncpg://username:password@localhost:5432/vd_index"

    # Redis配置
    redis_url: str = "redis://127.0.0.1:6379/0"
    
    # 头像文件存储
    avatar_root: str = "./static/avatars/mems"
    
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

    # 缓存配置
    cache_max_size: int = 10000
    cache_default_ttl: int = 300  # 5分钟
    cache_stats_ttl: int = 60     # 统计数据缓存1分钟
    cache_member_ttl: int = 300   # 成员数据缓存5分钟
    cache_activity_ttl: int = 300 # 活动数据缓存5分钟

    # 超级用户配置
    super_user_username: str = "admin"
    super_user_password: str = "admin123"
    super_user_email: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ConfigService:
    """配置服务类"""
    
    name = "config_service"
    
    def __init__(self):
        """初始化配置服务"""
        self._settings = None
    
    def get_settings(self) -> Settings:
        """获取应用设置"""
        if self._settings is None:
            self._settings = Settings()
        return self._settings
    
    def ensure_secret_key(self) -> str:
        """确保密钥文件存在，如果不存在则生成"""
        settings = self.get_settings()
        secret_file = Path(settings.secret_key_file)

        logger.debug(f"[CONFIG] 检查密钥文件: {secret_file}")
        logger.debug(f"[CONFIG] 密钥文件存在: {secret_file.exists()}")

        if secret_file.exists():
            try:
                key_content = secret_file.read_text().strip()
                logger.debug(f"[CONFIG] 从文件读取密钥，长度: {len(key_content)}")
                logger.debug(f"[CONFIG] 密钥前10字符: {key_content[:10]}...")
                return key_content
            except Exception as e:
                logger.error(f"[CONFIG] 读取密钥文件失败: {e}")
                raise

        # 生成新的密钥
        logger.info("[CONFIG] 密钥文件不存在，生成新密钥")
        secret_key = secrets.token_urlsafe(32)
        logger.debug(f"[CONFIG] 生成的密钥长度: {len(secret_key)}")

        # 确保目录存在
        secret_file.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"[CONFIG] 确保目录存在: {secret_file.parent}")

        # 写入密钥文件
        try:
            secret_file.write_text(secret_key)
            logger.info(f"[CONFIG] 密钥文件写入成功: {secret_file}")
        except Exception as e:
            logger.error(f"[CONFIG] 写入密钥文件失败: {e}")
            raise

        # 设置文件权限（仅所有者可读写）
        try:
            secret_file.chmod(0o600)
            logger.debug("[CONFIG] 密钥文件权限设置成功")
        except Exception as e:
            logger.warning(f"[CONFIG] 设置密钥文件权限失败: {e}")

        return secret_key

    def get_or_create_aes_key(self) -> str:
        """获取或创建AES加密密钥"""
        settings = self.get_settings()

        logger.debug("[CONFIG] 获取AES加密密钥")
        logger.debug(f"[CONFIG] 环境变量UIN_AES_KEY是否设置: {bool(settings.uin_aes_key)}")

        # 优先使用环境变量
        if settings.uin_aes_key:
            logger.info("[CONFIG] 使用环境变量中的AES密钥")
            logger.debug(f"[CONFIG] 环境变量密钥长度: {len(settings.uin_aes_key)}")
            logger.debug(f"[CONFIG] 环境变量密钥前10字符: {settings.uin_aes_key[:10]}...")
            return settings.uin_aes_key

        # 否则使用密钥文件
        logger.info("[CONFIG] 使用密钥文件中的AES密钥")
        return self.ensure_secret_key()
