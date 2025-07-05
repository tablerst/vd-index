#!/usr/bin/env python3
"""
快速头像测试脚本
用于快速诊断头像获取问题
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings
from core.crypto import decrypt_uin
from services.database.factory import DatabaseServiceFactory
from services.deps import set_database_service


async def quick_test():
    """快速测试"""
    print("=" * 50)
    print("快速头像测试")
    print("=" * 50)
    
    # 基本信息
    print(f"当前目录: {os.getcwd()}")
    print(f"调试模式: {settings.debug}")
    print(f"数据库URL: {settings.database_url}")
    print(f"头像目录: {settings.avatar_root}")
    print()
    
    # 检查密钥
    print("检查加密密钥...")
    try:
        from core.config import get_or_create_aes_key
        key = get_or_create_aes_key()
        print(f"✅ 密钥获取成功，长度: {len(key)}")
        print(f"密钥前10字符: {key[:10]}...")
    except Exception as e:
        print(f"❌ 密钥获取失败: {e}")
        return
    print()
    
    # 检查头像目录
    print("检查头像目录...")
    avatar_dir = Path(settings.avatar_root)
    if avatar_dir.exists():
        files = list(avatar_dir.glob("*.webp"))
        print(f"✅ 头像目录存在，文件数量: {len(files)}")
        if len(files) <= 5:
            print(f"文件列表: {[f.name for f in files]}")
    else:
        print(f"❌ 头像目录不存在: {avatar_dir}")
    print()
    
    # 测试数据库连接
    print("测试数据库连接...")
    try:
        factory = DatabaseServiceFactory()
        db_service = factory.create(settings.database_url)
        set_database_service(db_service)
        print("✅ 数据库服务初始化成功")
        
        from services.deps import get_session
        from backend.services.database.models.member.base import Member
        from sqlmodel import select
        
        async for session in get_session():
            result = await session.exec(select(Member).limit(1))
            member = result.first()
            
            if member:
                print(f"✅ 找到测试成员: {member.display_name}")
                print(f"成员ID: {member.id}")
                print(f"加密UIN长度: {len(member.uin_encrypted) if member.uin_encrypted else 0}")
                print(f"Salt: {member.salt}")
                
                # 测试解密
                try:
                    uin = decrypt_uin(member.uin_encrypted, member.salt)
                    print(f"✅ UIN解密成功: {uin}")
                    
                    # 检查头像文件
                    avatar_path = avatar_dir / f"{uin}.webp"
                    if avatar_path.exists():
                        print(f"✅ 头像文件存在: {avatar_path}")
                    else:
                        print(f"❌ 头像文件不存在: {avatar_path}")
                        
                except Exception as e:
                    print(f"❌ UIN解密失败: {e}")
                    
            else:
                print("❌ 数据库中没有成员数据")
            break
            
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
    
    print()
    print("=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(quick_test())
