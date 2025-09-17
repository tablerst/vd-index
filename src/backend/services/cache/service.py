"""
通用缓存服务
基于cachetools.TTLCache实现的异步安全缓存服务
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import logging
from typing import TypeVar, Callable, Awaitable, Optional, Any, Dict, List, Union
from functools import wraps
from datetime import datetime, timedelta

from cashews import cache as C
from services.cache.keys import L1_PREFIX
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T")

# 默认配置
DEFAULT_TTL = 300  # 5分钟
DEFAULT_MAX_SIZE = 10000
STATS_TTL = 60  # 统计数据缓存1分钟


class CacheStats(BaseModel):
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    cache_size: int = 0
    max_size: int = 0
    last_updated: datetime


class CacheService:
    """通用缓存服务（cashews 两级：L1 本地 + L2 Redis）"""
    
    def __init__(self, max_size: int = DEFAULT_MAX_SIZE, default_ttl: int = DEFAULT_TTL, negative_ttl: int = 30):
        """初始化缓存服务
        
        Args:
            max_size: 缓存最大容量（用于统计显示）
            default_ttl: 默认TTL（秒）
            negative_ttl: 负面缓存TTL（秒），当结果为空时使用
        """
        self._lock = asyncio.Lock()
        self._stats = CacheStats(max_size=max_size, last_updated=datetime.now())
        self._default_ttl = default_ttl
        self._negative_ttl = negative_ttl
        
        logger.info(f"CacheService initialized with max_size={max_size}, default_ttl={default_ttl}")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成稳定的缓存键
        
        Args:
            prefix: 键前缀
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            生成的缓存键
        """
        # 创建一个稳定的字符串表示
        key_parts = [prefix]
        
        # 处理位置参数
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # 对复杂对象进行JSON序列化并哈希
                try:
                    serialized = json.dumps(arg, sort_keys=True, default=str)
                    key_parts.append(hashlib.md5(serialized.encode()).hexdigest()[:8])
                except (TypeError, ValueError):
                    key_parts.append(str(hash(str(arg))))
        
        # 处理关键字参数
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                key_parts.append(f"{k}={v}")
        
        return ":".join(key_parts)
    
    async def get(self, key: str) -> Optional[T]:
        """获取缓存值（优先 L1，本地 miss 则查 L2，并回填 L1）"""
        # 先读 L1（本地内存）
        value = await C.get(f"{L1_PREFIX}{key}")
        if value is None:
            # 再读 L2（Redis）
            value = await C.get(key)
            # 命中 L2 时回填 L1
            if value is not None:
                await C.set(f"{L1_PREFIX}{key}", value, expire=self._default_ttl)

        # 更新统计
        self._stats.total_requests += 1
        if value is not None:
            self._stats.hits += 1
            logger.debug(f"Cache hit for key: {key}")
        else:
            self._stats.misses += 1
            logger.debug(f"Cache miss for key: {key}")

        # 更新命中率/时间
        self._stats.hit_rate = self._stats.hits / self._stats.total_requests if self._stats.total_requests > 0 else 0.0
        self._stats.last_updated = datetime.now()

        return value
    
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """设置缓存值（双写：先 L2，再 L1）"""
        expire = ttl if ttl is not None else self._default_ttl
        await C.set(key, value, expire=expire)
        await C.set(f"{L1_PREFIX}{key}", value, expire=min(expire, self._default_ttl))
        self._stats.last_updated = datetime.now()
        logger.debug(f"Cache set for key: {key}, ttl: {expire}")
    
    async def delete(self, key: str) -> bool:
        """删除缓存值（双删：L1 与 L2）"""
        await C.delete(f"{L1_PREFIX}{key}")
        await C.delete(key)
        self._stats.last_updated = datetime.now()
        logger.debug(f"Cache deleted for key: {key}")
        return True
    
    async def clear(self) -> None:
        """清空缓存（所有已配置后端）"""
        await C.clear()
        self._stats.cache_size = 0
        self._stats.last_updated = datetime.now()
        logger.info("Cache cleared")
    
    async def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        async with self._lock:
            return self._stats.model_copy()
    
    async def get_many(self, keys: List[str]) -> Dict[str, Optional[T]]:
        """批量获取缓存值
        
        Args:
            keys: 缓存键列表
            
        Returns:
            键值对字典
        """
        result = {}
        for key in keys:
            result[key] = await self.get(key)
        return result
    
    async def set_many(self, items: Dict[str, T], ttl: Optional[int] = None) -> None:
        """批量设置缓存值
        
        Args:
            items: 键值对字典
            ttl: 生存时间（秒）
        """
        for key, value in items.items():
            await self.set(key, value, ttl)
    
    def cached(self, ttl: int = DEFAULT_TTL, key_prefix: str = "", *, lock: bool = False):
        """缓存装饰器
        
        Args:
            ttl: 缓存生存时间（秒）
            key_prefix: 缓存键前缀
            lock: 是否启用并发锁防击穿
            
        Returns:
            装饰器函数
        """
        def decorator(fn: Callable[..., Awaitable[T]]):
            @wraps(fn)
            async def wrapper(*args, **kwargs) -> T:
                # 生成缓存键
                prefix = key_prefix or fn.__name__
                cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # 两级读取
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                async def _compute_and_fill():
                    result = await fn(*args, **kwargs)
                    expire = ttl if result is not None else self._negative_ttl
                    await self.set(cache_key, result, ttl=expire)
                    return result

                if lock:
                    locked_compute = C.locked(ttl="30s")(_compute_and_fill)
                    return await locked_compute()
                return await _compute_and_fill()
            return wrapper
        return decorator


# 全局缓存服务实例
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """获取缓存服务实例"""
    global _cache_service
    if _cache_service is None:
        raise ValueError("Cache service not initialized. Call set_cache_service() first.")
    return _cache_service


def set_cache_service(cache_service: CacheService) -> None:
    """设置缓存服务实例"""
    global _cache_service
    _cache_service = cache_service


def clear_cache_service() -> None:
    """清除缓存服务实例（主要用于测试）"""
    global _cache_service
    _cache_service = None
