"""
缓存服务模块
"""
from .service import CacheService, CacheStats, get_cache_service, set_cache_service, clear_cache_service
from .factory import CacheServiceFactory

__all__ = [
    "CacheService",
    "CacheStats",
    "CacheServiceFactory",
    "get_cache_service",
    "set_cache_service",
    "clear_cache_service"
]
