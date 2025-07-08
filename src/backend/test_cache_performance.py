#!/usr/bin/env python3
"""
缓存性能测试脚本
测试缓存优化前后的性能差异
"""
import asyncio
import time
import statistics
from typing import List
from contextlib import asynccontextmanager

from services.database.service import DatabaseService
from services.database.factory import DatabaseServiceFactory
from services.cache.factory import CacheServiceFactory
from services.config.factory import ConfigServiceFactory
from services.deps import set_database_service, set_cache_service, set_config_service
from services.database.models.member.crud import MemberCRUD
from services.database.models.activity.crud import ActivityCRUD
from api.v1.activities import build_activity_response


async def setup_services():
    """初始化服务"""
    # 初始化配置服务
    config_factory = ConfigServiceFactory()
    config_service = config_factory.create()
    set_config_service(config_service)
    settings = config_service.get_settings()

    # 初始化缓存服务
    cache_factory = CacheServiceFactory()
    cache_service = cache_factory.create(config_service=config_service)
    set_cache_service(cache_service)

    # 初始化数据库服务
    db_factory = DatabaseServiceFactory()
    db_service = db_factory.create(settings.database_url)
    set_database_service(db_service)

    return db_service, cache_service


async def test_member_get_performance(session, member_ids: List[int], iterations: int = 100):
    """测试成员获取性能"""
    print(f"\n🧪 测试成员获取性能 (ID数量: {len(member_ids)}, 迭代次数: {iterations})")
    
    # 清空缓存
    from services.deps import get_cache_service
    cache_service = get_cache_service()
    await cache_service.clear()
    
    # 测试单次获取（无缓存）
    times_no_cache = []
    for _ in range(iterations):
        start_time = time.time()
        for member_id in member_ids:
            await MemberCRUD.get_by_id(session, member_id)
        end_time = time.time()
        times_no_cache.append(end_time - start_time)
    
    # 预热缓存
    for member_id in member_ids:
        await MemberCRUD.get_by_id(session, member_id)
    
    # 测试单次获取（有缓存）
    times_with_cache = []
    for _ in range(iterations):
        start_time = time.time()
        for member_id in member_ids:
            await MemberCRUD.get_by_id(session, member_id)
        end_time = time.time()
        times_with_cache.append(end_time - start_time)
    
    # 清空缓存
    await cache_service.clear()
    
    # 测试批量获取（无缓存）
    times_batch_no_cache = []
    for _ in range(iterations):
        start_time = time.time()
        await MemberCRUD.get_many_by_ids(session, member_ids)
        end_time = time.time()
        times_batch_no_cache.append(end_time - start_time)
    
    # 预热缓存
    await MemberCRUD.get_many_by_ids(session, member_ids)
    
    # 测试批量获取（有缓存）
    times_batch_with_cache = []
    for _ in range(iterations):
        start_time = time.time()
        await MemberCRUD.get_many_by_ids(session, member_ids)
        end_time = time.time()
        times_batch_with_cache.append(end_time - start_time)
    
    # 输出结果
    print(f"📊 单次获取性能对比:")
    print(f"   无缓存: {statistics.mean(times_no_cache):.4f}s ± {statistics.stdev(times_no_cache):.4f}s")
    print(f"   有缓存: {statistics.mean(times_with_cache):.4f}s ± {statistics.stdev(times_with_cache):.4f}s")
    print(f"   性能提升: {statistics.mean(times_no_cache) / statistics.mean(times_with_cache):.2f}x")
    
    print(f"📊 批量获取性能对比:")
    print(f"   无缓存: {statistics.mean(times_batch_no_cache):.4f}s ± {statistics.stdev(times_batch_no_cache):.4f}s")
    print(f"   有缓存: {statistics.mean(times_batch_with_cache):.4f}s ± {statistics.stdev(times_batch_with_cache):.4f}s")
    print(f"   性能提升: {statistics.mean(times_batch_no_cache) / statistics.mean(times_batch_with_cache):.2f}x")


async def test_activity_response_performance(session, activity_ids: List[int], iterations: int = 50):
    """测试活动响应构建性能"""
    print(f"\n🧪 测试活动响应构建性能 (活动数量: {len(activity_ids)}, 迭代次数: {iterations})")
    
    # 清空缓存
    from services.deps import get_cache_service
    cache_service = get_cache_service()
    await cache_service.clear()
    
    # 获取活动对象
    activities = []
    for activity_id in activity_ids:
        activity = await ActivityCRUD.get_by_id(session, activity_id)
        if activity:
            activities.append(activity)
    
    if not activities:
        print("❌ 没有找到活动数据，跳过测试")
        return
    
    # 测试无缓存性能
    times_no_cache = []
    for _ in range(iterations):
        await cache_service.clear()  # 确保每次都是无缓存状态
        start_time = time.time()
        for activity in activities:
            await build_activity_response(activity, session)
        end_time = time.time()
        times_no_cache.append(end_time - start_time)
    
    # 预热缓存
    for activity in activities:
        await build_activity_response(activity, session)
    
    # 测试有缓存性能
    times_with_cache = []
    for _ in range(iterations):
        start_time = time.time()
        for activity in activities:
            await build_activity_response(activity, session)
        end_time = time.time()
        times_with_cache.append(end_time - start_time)
    
    # 输出结果
    print(f"📊 活动响应构建性能对比:")
    print(f"   无缓存: {statistics.mean(times_no_cache):.4f}s ± {statistics.stdev(times_no_cache):.4f}s")
    print(f"   有缓存: {statistics.mean(times_with_cache):.4f}s ± {statistics.stdev(times_with_cache):.4f}s")
    print(f"   性能提升: {statistics.mean(times_no_cache) / statistics.mean(times_with_cache):.2f}x")


async def main():
    """主测试函数"""
    print("🚀 开始缓存性能测试...")
    
    # 初始化服务
    db_service, cache_service = await setup_services()
    
    try:
        async with db_service.with_session() as session:
            # 获取一些测试数据
            print("📋 准备测试数据...")
            
            # 获取前20个成员ID
            members = await MemberCRUD.get_paginated(session, page=1, page_size=20)
            member_ids = [member.id for member in members[0]]
            
            # 获取前5个活动ID
            activities = await ActivityCRUD.get_paginated(session, page=1, page_size=5)
            activity_ids = [activity.id for activity in activities[0]]
            
            print(f"✅ 找到 {len(member_ids)} 个成员和 {len(activity_ids)} 个活动")
            
            if member_ids:
                await test_member_get_performance(session, member_ids)
            
            if activity_ids:
                await test_activity_response_performance(session, activity_ids)
            
            # 显示缓存统计
            stats = await cache_service.get_stats()
            print(f"\n📈 缓存统计信息:")
            print(f"   总请求数: {stats.total_requests}")
            print(f"   命中数: {stats.hits}")
            print(f"   未命中数: {stats.misses}")
            print(f"   命中率: {stats.hit_rate:.2%}")
            print(f"   缓存大小: {stats.cache_size}/{stats.max_size}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db_service.teardown()
        print("\n✅ 缓存性能测试完成")


if __name__ == "__main__":
    asyncio.run(main())
