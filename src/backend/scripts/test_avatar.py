#!/usr/bin/env python3
"""
测试头像解密脚本
"""
import asyncio
from pathlib import Path
import sys

# 添加父目录到Python路径
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

from core.crypto import decrypt_uin
from services.deps import set_database_service
from services.database.service import DatabaseService
from backend.services.database.models.member import Member
from core.config import settings


async def test_avatar_decryption():
    """测试头像解密"""
    # 初始化数据库服务
    db_service = DatabaseService(settings.database_url)
    set_database_service(db_service)
    
    async with db_service.with_session() as session:
        # 查询成员83
        member = await session.get(Member, 83)
        if not member:
            print("成员83不存在")
            return
        
        print(f"成员ID: {member.id}")
        print(f"成员名称: {member.display_name}")
        print(f"加密UIN: {member.uin_encrypted}")
        print(f"Salt: {member.salt}")
        print(f"Avatar root配置: {settings.avatar_root}")
        
        # 解密UIN
        try:
            uin = decrypt_uin(member.uin_encrypted, member.salt)
            print(f"解密后UIN: {uin}")
            
            # 检查头像文件
            avatar_path = Path(settings.avatar_root) / f"{uin}.webp"
            print(f"头像文件路径: {avatar_path}")
            print(f"头像文件存在: {avatar_path.exists()}")
            
            if avatar_path.exists():
                print(f"文件大小: {avatar_path.stat().st_size} bytes")
            else:
                # 列出所有可用的头像文件
                avatar_dir = Path(settings.avatar_root)
                if avatar_dir.exists():
                    print(f"\n可用的头像文件:")
                    for file in sorted(avatar_dir.glob("*.webp")):
                        print(f"  {file.name}")
                
        except Exception as e:
            print(f"解密失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_avatar_decryption())
