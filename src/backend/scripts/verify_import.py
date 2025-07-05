#!/usr/bin/env python3
"""
验证导入数据的脚本（异步版本）
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import select
from backend.services.database.models.member import Member
from services.database.factory import DatabaseServiceFactory
from services.deps import set_database_service, session_scope
from core.config import settings


async def verify_import():
    """验证导入的数据（异步版本）"""
    # 初始化数据库服务
    factory = DatabaseServiceFactory()
    db_service = factory.create(settings.database_url)
    set_database_service(db_service)
    
    try:
        async with session_scope() as session:
            # 查询所有成员
            result = await session.exec(select(Member))
            members = result.all()
            
            print(f'数据库中共有 {len(members)} 个成员')
            
            # 显示前5个成员的详细信息
            print('\n前5个成员详情:')
            for i, member in enumerate(members[:5]):
                print(f'{i+1}. ID: {member.id}')
                print(f'   显示名称: {member.display_name}')
                print(f'   群昵称: {member.group_nick}')
                print(f'   QQ昵称: {member.qq_nick}')
                print(f'   角色: {member.role}')
                print(f'   入群时间: {member.join_time}')
                print(f'   等级积分: {member.level_point}')
                print(f'   等级: {member.level_value}')
                print(f'   Q龄: {member.q_age}')
                print(f'   头像哈希: {member.avatar_hash[:16]}...')
                print()
            
            # 统计角色分布
            role_counts = {}
            for member in members:
                role_counts[member.role] = role_counts.get(member.role, 0) + 1
            
            print('角色分布:')
            role_names = {0: '群主', 1: '管理员', 2: '群员'}
            for role, count in role_counts.items():
                print(f'  {role_names.get(role, f"角色{role}")}: {count}人')
                
    finally:
        # 清理数据库服务
        await db_service.teardown()


if __name__ == "__main__":
    asyncio.run(verify_import())
