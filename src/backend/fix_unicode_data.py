#!/usr/bin/env python3
"""
修复数据库中activity表tags字段的Unicode编码问题
将Unicode转义字符转换回正常的中文字符
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

async def fix_unicode_data():
    """修复数据库中的Unicode编码数据"""
    try:
        config_factory = ConfigServiceFactory()
        config_service = config_factory.create()
        config = config_service.get_settings()
        
        # 从数据库URL中提取连接信息
        db_url = config.database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        print(f'连接数据库: {db_url.split("@")[1] if "@" in db_url else "localhost"}')
        conn = await asyncpg.connect(db_url)
        
        # 查询所有包含Unicode转义的活动记录
        rows = await conn.fetch('SELECT id, title, tags, participant_ids FROM activities ORDER BY id')
        
        print('=== 开始修复Unicode编码数据 ===')
        if not rows:
            print('✅ 数据库中没有活动记录')
            await conn.close()
            return
            
        fixed_count = 0
        total_count = len(rows)
        
        for row in rows:
            activity_id = row["id"]
            title = row["title"]
            tags_raw = row["tags"]
            participant_ids_raw = row["participant_ids"]
            
            print(f'\n处理活动 ID {activity_id}: {title}')
            
            # 处理tags字段
            tags_fixed = False
            if isinstance(tags_raw, str) and '\\u' in tags_raw:
                try:
                    # 解析JSON并重新序列化（不转义Unicode）
                    parsed_tags = json.loads(tags_raw)
                    fixed_tags = json.dumps(parsed_tags, ensure_ascii=False, separators=(',', ':'))
                    
                    print(f'  Tags 原始: {tags_raw}')
                    print(f'  Tags 修复: {fixed_tags}')
                    tags_fixed = True
                except json.JSONDecodeError as e:
                    print(f'  ❌ Tags JSON解析失败: {e}')
                    continue
            else:
                fixed_tags = tags_raw
                print(f'  Tags 无需修复: {tags_raw}')
            
            # 处理participant_ids字段
            participant_ids_fixed = False
            if isinstance(participant_ids_raw, str) and '\\u' in participant_ids_raw:
                try:
                    # 解析JSON并重新序列化（不转义Unicode）
                    parsed_participant_ids = json.loads(participant_ids_raw)
                    fixed_participant_ids = json.dumps(parsed_participant_ids, ensure_ascii=False, separators=(',', ':'))
                    
                    print(f'  Participant IDs 原始: {participant_ids_raw}')
                    print(f'  Participant IDs 修复: {fixed_participant_ids}')
                    participant_ids_fixed = True
                except json.JSONDecodeError as e:
                    print(f'  ❌ Participant IDs JSON解析失败: {e}')
                    continue
            else:
                fixed_participant_ids = participant_ids_raw
                print(f'  Participant IDs 无需修复: {participant_ids_raw}')
            
            # 如果有字段需要修复，则更新数据库
            if tags_fixed or participant_ids_fixed:
                try:
                    await conn.execute(
                        'UPDATE activities SET tags = $1, participant_ids = $2 WHERE id = $3',
                        fixed_tags, fixed_participant_ids, activity_id
                    )
                    print(f'  ✅ 成功更新活动 {activity_id}')
                    fixed_count += 1
                except Exception as e:
                    print(f'  ❌ 更新活动 {activity_id} 失败: {e}')
            else:
                print(f'  ℹ️  活动 {activity_id} 无需修复')
        
        await conn.close()
        
        # 总结报告
        print('\n' + '='*60)
        print('=== 修复完成总结 ===')
        print(f'总活动数: {total_count}')
        print(f'修复活动数: {fixed_count}')
        print(f'无需修复: {total_count - fixed_count}')
        
        if fixed_count > 0:
            print(f'✅ 成功修复 {fixed_count} 个活动的Unicode编码问题')
        else:
            print('ℹ️  没有发现需要修复的Unicode编码问题')
            
        return fixed_count
        
    except Exception as e:
        print(f'❌ 修复过程中发生错误: {e}')
        import traceback
        traceback.print_exc()
        return 0

async def verify_fix():
    """验证修复结果"""
    print('\n' + '='*60)
    print('=== 验证修复结果 ===')
    
    try:
        config_factory = ConfigServiceFactory()
        config_service = config_factory.create()
        config = config_service.get_settings()
        
        # 从数据库URL中提取连接信息
        db_url = config.database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        conn = await asyncpg.connect(db_url)
        
        # 查询所有活动的tags字段
        rows = await conn.fetch('SELECT id, title, tags FROM activities ORDER BY id LIMIT 10')
        
        unicode_issues = []
        
        for row in rows:
            tags_data = row["tags"]
            if isinstance(tags_data, str) and '\\u' in tags_data:
                unicode_issues.append({
                    'id': row["id"],
                    'title': row["title"],
                    'tags': tags_data
                })
        
        await conn.close()
        
        if unicode_issues:
            print(f'❌ 仍然发现 {len(unicode_issues)} 个Unicode编码问题:')
            for issue in unicode_issues:
                print(f'  - ID {issue["id"]}: {issue["title"]}')
                print(f'    Tags: {issue["tags"]}')
        else:
            print('✅ 验证通过！所有Unicode编码问题已修复')
            
        return len(unicode_issues) == 0
        
    except Exception as e:
        print(f'❌ 验证过程中发生错误: {e}')
        return False

async def main():
    """主函数"""
    print("开始修复activity表中的Unicode编码问题...")
    
    # 执行修复
    fixed_count = await fix_unicode_data()
    
    # 验证修复结果
    if fixed_count > 0:
        success = await verify_fix()
        if success:
            print('\n🎉 所有Unicode编码问题已成功修复！')
        else:
            print('\n⚠️  修复过程中可能存在问题，请检查日志')
    else:
        print('\n✅ 没有发现需要修复的问题')

if __name__ == "__main__":
    asyncio.run(main())
