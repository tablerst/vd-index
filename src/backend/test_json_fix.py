#!/usr/bin/env python3
"""
测试JSON序列化修复是否有效
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from services.config.factory import ConfigServiceFactory
from services.database.factory import DatabaseServiceFactory
from services.database.models.activity.base import Activity, UnicodePreservingJSON
from datetime import datetime

async def test_json_serialization():
    """测试JSON序列化是否正确处理中文字符"""
    
    # 测试自定义JSON类型
    json_type = UnicodePreservingJSON()
    
    # 测试数据
    test_tags = ["中文标签", "技术", "分享", "English"]
    
    print("=== 测试自定义JSON类型 ===")
    print(f"原始数据: {test_tags}")
    
    # 测试序列化
    serialized = json_type.process_bind_param(test_tags, None)
    print(f"序列化结果: {serialized}")
    print(f"序列化类型: {type(serialized)}")
    
    # 检查是否包含Unicode转义
    if '\\u' in serialized:
        print("❌ 仍然包含Unicode转义字符!")
    else:
        print("✅ 中文字符保持原样，没有被转义")
    
    # 测试反序列化
    deserialized = json_type.process_result_value(serialized, None)
    print(f"反序列化结果: {deserialized}")
    print(f"反序列化类型: {type(deserialized)}")
    
    # 验证数据完整性
    if deserialized == test_tags:
        print("✅ 数据完整性验证通过")
    else:
        print("❌ 数据完整性验证失败")
    
    print("\n" + "="*60)
    
    # 测试数据库操作
    try:
        config_factory = ConfigServiceFactory()
        config_service = config_factory.create()
        settings = config_service.get_settings()
        
        db_factory = DatabaseServiceFactory()
        db_service = db_factory.create(settings.database_url)
        
        print("=== 测试数据库操作 ===")
        
        async with db_service.with_session() as session:
            # 创建测试活动
            test_activity = Activity(
                title="JSON序列化测试活动",
                description="测试中文标签是否正确存储",
                date=datetime.now(),
                tags=["测试", "中文", "JSON序列化", "修复"],
                participant_ids=[1, 2, 3]
            )
            
            session.add(test_activity)
            await session.commit()
            await session.refresh(test_activity)
            
            print(f"✅ 成功创建测试活动，ID: {test_activity.id}")
            print(f"存储的标签: {test_activity.tags}")
            
            # 查询验证
            from sqlmodel import select
            statement = select(Activity).where(Activity.id == test_activity.id)
            result = await session.exec(statement)
            retrieved_activity = result.first()
            
            if retrieved_activity:
                print(f"✅ 成功查询活动")
                print(f"查询到的标签: {retrieved_activity.tags}")
                
                # 验证标签是否正确
                expected_tags = ["测试", "中文", "JSON序列化", "修复"]
                if retrieved_activity.tags == expected_tags:
                    print("✅ 标签数据完整性验证通过")
                else:
                    print("❌ 标签数据完整性验证失败")
                    print(f"期望: {expected_tags}")
                    print(f"实际: {retrieved_activity.tags}")
            else:
                print("❌ 查询活动失败")
                
            # 清理测试数据
            await session.delete(test_activity)
            await session.commit()
            print("✅ 清理测试数据完成")
            
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_json_serialization())
