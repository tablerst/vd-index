#!/usr/bin/env python3
"""
测试缓存修复是否正常工作
"""
import asyncio
from services.cache.service import CacheService


async def test_cache_fix():
    """测试缓存修复"""
    print("🧪 测试缓存修复...")
    
    # 创建缓存服务
    cache_service = CacheService(max_size=100, default_ttl=60)
    
    # 测试1: 普通缓存（使用默认TTL）
    print("\n📋 测试1: 普通缓存")
    await cache_service.set("normal_key", {"data": "normal_value"})
    result1 = await cache_service.get("normal_key")
    print(f"   设置: {{'data': 'normal_value'}}")
    print(f"   获取: {result1}")
    print(f"   类型: {type(result1)}")
    
    # 测试2: 自定义TTL缓存
    print("\n📋 测试2: 自定义TTL缓存")
    await cache_service.set("custom_ttl_key", {"data": "custom_value"}, ttl=30)
    result2 = await cache_service.get("custom_ttl_key")
    print(f"   设置: {{'data': 'custom_value'}} (TTL=30)")
    print(f"   获取: {result2}")
    print(f"   类型: {type(result2)}")
    
    # 测试3: 批量操作
    print("\n📋 测试3: 批量操作")
    items = {
        "batch_key1": {"id": 1, "name": "item1"},
        "batch_key2": {"id": 2, "name": "item2"}
    }
    await cache_service.set_many(items, ttl=45)
    results = await cache_service.get_many(["batch_key1", "batch_key2", "nonexistent"])
    print(f"   设置: {items}")
    print(f"   获取: {results}")
    
    # 测试4: 统计信息
    print("\n📋 测试4: 统计信息")
    stats = await cache_service.get_stats()
    print(f"   总请求: {stats.total_requests}")
    print(f"   命中: {stats.hits}")
    print(f"   未命中: {stats.misses}")
    print(f"   命中率: {stats.hit_rate:.2%}")
    print(f"   缓存大小: {stats.cache_size}")
    
    # 测试5: 过期测试（短TTL）
    print("\n📋 测试5: 过期测试")
    await cache_service.set("expire_key", {"data": "will_expire"}, ttl=1)
    result_before = await cache_service.get("expire_key")
    print(f"   立即获取: {result_before}")
    
    print("   等待2秒...")
    await asyncio.sleep(2)
    
    result_after = await cache_service.get("expire_key")
    print(f"   2秒后获取: {result_after}")
    
    print("\n✅ 缓存修复测试完成!")


if __name__ == "__main__":
    asyncio.run(test_cache_fix())
