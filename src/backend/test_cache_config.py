#!/usr/bin/env python3
"""
缓存配置验证脚本
验证缓存配置是否正确加载和应用
"""
import asyncio
from services.config.factory import ConfigServiceFactory
from services.cache.factory import CacheServiceFactory


async def test_cache_config():
    """测试缓存配置"""
    print("🧪 测试缓存配置...")
    
    # 初始化配置服务
    config_factory = ConfigServiceFactory()
    config_service = config_factory.create()
    settings = config_service.get_settings()
    
    print(f"📋 当前缓存配置:")
    print(f"   CACHE_MAX_SIZE: {settings.cache_max_size}")
    print(f"   CACHE_DEFAULT_TTL: {settings.cache_default_ttl}秒")
    print(f"   CACHE_STATS_TTL: {settings.cache_stats_ttl}秒")
    print(f"   CACHE_MEMBER_TTL: {settings.cache_member_ttl}秒")
    print(f"   CACHE_ACTIVITY_TTL: {settings.cache_activity_ttl}秒")
    
    # 使用配置创建缓存服务
    cache_factory = CacheServiceFactory()
    cache_service = cache_factory.create(config_service=config_service)
    
    print(f"\n✅ 缓存服务创建成功:")
    print(f"   实际最大容量: {cache_service._cache.maxsize}")
    print(f"   实际默认TTL: {cache_service._default_ttl}秒")
    
    # 测试缓存基本功能
    await cache_service.set("test_key", "test_value")
    value = await cache_service.get("test_key")
    
    if value == "test_value":
        print("✅ 缓存基本功能正常")
    else:
        print("❌ 缓存基本功能异常")
    
    # 获取统计信息
    stats = await cache_service.get_stats()
    print(f"\n📊 缓存统计:")
    print(f"   缓存大小: {stats.cache_size}/{stats.max_size}")
    print(f"   总请求数: {stats.total_requests}")
    print(f"   命中率: {stats.hit_rate:.2%}")
    
    print("\n🎉 缓存配置验证完成!")


if __name__ == "__main__":
    asyncio.run(test_cache_config())
