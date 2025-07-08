"""
缓存服务测试
"""
import pytest
import asyncio
from datetime import datetime

from services.cache.service import CacheService


@pytest.fixture
async def cache_service():
    """创建缓存服务实例"""
    service = CacheService(max_size=100, default_ttl=60)
    yield service
    await service.clear()


@pytest.mark.asyncio
async def test_basic_cache_operations(cache_service):
    """测试基本缓存操作"""
    # 测试设置和获取
    await cache_service.set("test_key", "test_value")
    value = await cache_service.get("test_key")
    assert value == "test_value"
    
    # 测试不存在的键
    value = await cache_service.get("nonexistent_key")
    assert value is None
    
    # 测试删除
    deleted = await cache_service.delete("test_key")
    assert deleted is True
    
    value = await cache_service.get("test_key")
    assert value is None
    
    # 测试删除不存在的键
    deleted = await cache_service.delete("nonexistent_key")
    assert deleted is False


@pytest.mark.asyncio
async def test_cache_ttl(cache_service):
    """测试TTL功能"""
    # 设置短TTL
    await cache_service.set("ttl_key", "ttl_value", ttl=1)
    
    # 立即获取应该成功
    value = await cache_service.get("ttl_key")
    assert value == "ttl_value"
    
    # 等待TTL过期
    await asyncio.sleep(1.1)
    
    # 应该已经过期
    value = await cache_service.get("ttl_key")
    assert value is None


@pytest.mark.asyncio
async def test_batch_operations(cache_service):
    """测试批量操作"""
    # 批量设置
    items = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }
    await cache_service.set_many(items)
    
    # 批量获取
    keys = ["key1", "key2", "key3", "nonexistent"]
    results = await cache_service.get_many(keys)
    
    assert results["key1"] == "value1"
    assert results["key2"] == "value2"
    assert results["key3"] == "value3"
    assert results["nonexistent"] is None


@pytest.mark.asyncio
async def test_cache_stats(cache_service):
    """测试缓存统计"""
    # 初始统计
    stats = await cache_service.get_stats()
    assert stats.hits == 0
    assert stats.misses == 0
    assert stats.total_requests == 0
    assert stats.hit_rate == 0.0
    
    # 设置一些值
    await cache_service.set("stats_key1", "value1")
    await cache_service.set("stats_key2", "value2")
    
    # 命中测试
    await cache_service.get("stats_key1")  # 命中
    await cache_service.get("stats_key2")  # 命中
    await cache_service.get("nonexistent")  # 未命中
    
    stats = await cache_service.get_stats()
    assert stats.hits == 2
    assert stats.misses == 1
    assert stats.total_requests == 3
    assert stats.hit_rate == 2/3


@pytest.mark.asyncio
async def test_cache_decorator(cache_service):
    """测试缓存装饰器"""
    call_count = 0
    
    @cache_service.cached(ttl=60, key_prefix="test_func")
    async def expensive_function(x, y):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)  # 模拟耗时操作
        return x + y
    
    # 第一次调用
    result1 = await expensive_function(1, 2)
    assert result1 == 3
    assert call_count == 1
    
    # 第二次调用相同参数，应该从缓存获取
    result2 = await expensive_function(1, 2)
    assert result2 == 3
    assert call_count == 1  # 没有增加
    
    # 不同参数，应该重新计算
    result3 = await expensive_function(2, 3)
    assert result3 == 5
    assert call_count == 2


@pytest.mark.asyncio
async def test_cache_clear(cache_service):
    """测试清空缓存"""
    # 设置一些值
    await cache_service.set("clear_key1", "value1")
    await cache_service.set("clear_key2", "value2")
    
    # 确认值存在
    assert await cache_service.get("clear_key1") == "value1"
    assert await cache_service.get("clear_key2") == "value2"
    
    # 清空缓存
    await cache_service.clear()
    
    # 确认值已被清空
    assert await cache_service.get("clear_key1") is None
    assert await cache_service.get("clear_key2") is None
    
    # 统计也应该重置
    stats = await cache_service.get_stats()
    assert stats.cache_size == 0


@pytest.mark.asyncio
async def test_complex_data_types(cache_service):
    """测试复杂数据类型缓存"""
    # 测试字典
    dict_data = {"name": "test", "age": 25, "items": [1, 2, 3]}
    await cache_service.set("dict_key", dict_data)
    result = await cache_service.get("dict_key")
    assert result == dict_data
    
    # 测试列表
    list_data = [1, "two", {"three": 3}]
    await cache_service.set("list_key", list_data)
    result = await cache_service.get("list_key")
    assert result == list_data
    
    # 测试自定义对象（需要可序列化）
    class TestObject:
        def __init__(self, value):
            self.value = value
        
        def __eq__(self, other):
            return isinstance(other, TestObject) and self.value == other.value
    
    obj_data = TestObject("test_value")
    await cache_service.set("obj_key", obj_data)
    result = await cache_service.get("obj_key")
    assert result == obj_data


@pytest.mark.asyncio
async def test_key_generation(cache_service):
    """测试缓存键生成"""
    # 测试不同参数生成不同的键
    @cache_service.cached(ttl=60)
    async def test_func(a, b, c=None):
        return f"{a}-{b}-{c}"
    
    # 不同的调用应该生成不同的缓存键
    result1 = await test_func(1, 2)
    result2 = await test_func(1, 3)
    result3 = await test_func(1, 2, c="test")
    
    assert result1 == "1-2-None"
    assert result2 == "1-3-None"
    assert result3 == "1-2-test"
    
    # 相同参数应该返回缓存结果
    result4 = await test_func(1, 2)
    assert result4 == result1
