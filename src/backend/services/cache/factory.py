"""
缓存服务工厂
"""
from __future__ import annotations
from typing import Optional

from .service import CacheService, DEFAULT_TTL, DEFAULT_MAX_SIZE


class CacheServiceFactory:
    """缓存服务工厂类"""

    def __init__(self) -> None:
        self.service_class = CacheService

    def create(self, config_service=None, max_size: Optional[int] = None, default_ttl: Optional[int] = None) -> CacheService:
        """创建缓存服务实例

        Args:
            config_service: 配置服务实例（可选）
            max_size: 缓存最大容量（可选，优先使用配置服务）
            default_ttl: 默认TTL（秒）（可选，优先使用配置服务）

        Returns:
            CacheService: 缓存服务实例
        """
        # 如果提供了配置服务，从配置中读取参数
        if config_service is not None:
            settings = config_service.get_settings()
            max_size = max_size or settings.cache_max_size
            default_ttl = default_ttl or settings.cache_default_ttl
        else:
            # 使用默认值或传入的参数
            max_size = max_size or DEFAULT_MAX_SIZE
            default_ttl = default_ttl or DEFAULT_TTL

        # 传递负面缓存 TTL（如存在）
        negative_ttl = None
        if config_service is not None and hasattr(settings, "cache_negative_ttl"):
            negative_ttl = settings.cache_negative_ttl

        return CacheService(
            max_size=max_size,
            default_ttl=default_ttl,
            **({"negative_ttl": negative_ttl} if negative_ttl is not None else {})
        )
