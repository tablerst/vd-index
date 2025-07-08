#!/usr/bin/env python3
"""
检查数据库中activity表的tags字段是否存在Unicode编码问题
"""
import asyncio
import asyncpg
import json
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from services.config.factory import ConfigServiceFactory

async def check_activity_tags():
    """检查活动表中的tags字段是否存在Unicode编码问题"""
    try:
        config_factory = ConfigServiceFactory()
        config_service = config_factory.create()
        config = config_service.get_settings()
        # 从数据库URL中提取连接信息
        db_url = config.database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        print(f'连接数据库: {db_url.split("@")[1] if "@" in db_url else "localhost"}')
        conn = await asyncpg.connect(db_url)
        
        # 查询所有活动的tags字段
        rows = await conn.fetch('SELECT id, title, tags FROM activities ORDER BY id LIMIT 20')
        
        print('=== 活动表tags字段检查 ===')
        if not rows:
            print('✅ 数据库中没有活动记录')
            await conn.close()
            return
            
        unicode_issues = []
        
        for row in rows:
            print(f'\nID: {row["id"]}, Title: {row["title"]}')
            tags_data = row["tags"]
            print(f'Tags (type): {type(tags_data)}')
            
            # 检查不同的数据类型
            if isinstance(tags_data, str):
                print(f'Tags (string): {tags_data}')
                # 检查是否包含Unicode转义
                if '\\u' in tags_data:
                    print('⚠️  发现Unicode转义字符!')
                    unicode_issues.append({
                        'id': row["id"],
                        'title': row["title"],
                        'tags_raw': tags_data
                    })
                try:
                    parsed_tags = json.loads(tags_data)
                    print(f'Tags (parsed): {parsed_tags}')
                except json.JSONDecodeError as e:
                    print(f'❌ JSON解析失败: {e}')
            elif isinstance(tags_data, list):
                print(f'Tags (list): {tags_data}')
                # 检查列表中的每个元素
                for tag in tags_data:
                    if isinstance(tag, str) and '\\u' in tag:
                        print(f'⚠️  标签中发现Unicode转义: {tag}')
                        unicode_issues.append({
                            'id': row["id"],
                            'title': row["title"],
                            'problematic_tag': tag
                        })
            else:
                print(f'Tags (other): {tags_data}')
            
            print('-' * 60)
            
        await conn.close()
        
        # 总结报告
        print('\n=== 检查结果总结 ===')
        if unicode_issues:
            print(f'❌ 发现 {len(unicode_issues)} 个Unicode编码问题:')
            for issue in unicode_issues:
                print(f'  - ID {issue["id"]}: {issue["title"]}')
                if 'tags_raw' in issue:
                    print(f'    原始数据: {issue["tags_raw"]}')
                if 'problematic_tag' in issue:
                    print(f'    问题标签: {issue["problematic_tag"]}')
        else:
            print('✅ 未发现Unicode编码问题')
            
        return unicode_issues
        
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(check_activity_tags())
