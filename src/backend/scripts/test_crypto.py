#!/usr/bin/env python3
"""
测试加密解密功能（异步版本）
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import select
from services.database.models.member import Member
from services.database.factory import DatabaseServiceFactory
from services.deps import set_database_service, session_scope
from core.config import settings
from core.crypto import decrypt_uin


async def test_crypto():
    """测试加密解密功能（异步版本）"""
    # 初始化数据库服务
    factory = DatabaseServiceFactory()
    db_service = factory.create(settings.database_url)
    set_database_service(db_service)
    
    try:
        async with session_scope() as session:
            # 获取第一个成员进行测试
            result = await session.exec(select(Member))
            member = result.first()
            
            if not member:
                print("❌ 数据库中没有成员数据")
                return
            
            print(f"🔍 测试成员: {member.display_name}")
            print(f"   加密的UIN: {member.uin_encrypted[:50]}...")
            print(f"   盐值: {member.salt}")
            
            try:
                # 解密UIN
                decrypted_uin = decrypt_uin(member.uin_encrypted, member.salt)
                print(f"✅ 解密成功!")
                print(f"   解密后的UIN: {decrypted_uin}")
                
                # 验证头像哈希
                from core.crypto import generate_avatar_hash
                expected_hash = generate_avatar_hash(decrypted_uin, member.salt)
                
                if expected_hash == member.avatar_hash:
                    print(f"✅ 头像哈希验证成功!")
                else:
                    print(f"❌ 头像哈希验证失败!")
                    print(f"   期望: {expected_hash}")
                    print(f"   实际: {member.avatar_hash}")
                    
            except Exception as e:
                print(f"❌ 解密失败: {e}")
                
    finally:
        # 清理数据库服务
        await db_service.teardown()


if __name__ == "__main__":
    asyncio.run(test_crypto())
