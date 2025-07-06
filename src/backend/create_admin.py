#!/usr/bin/env python3
"""
创建管理员用户脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from core.database import get_async_session
from services.database.models.user import User, UserCRUD
from services.auth.service import AuthService
from services.config.factory import ConfigServiceFactory


async def create_admin_user():
    """创建管理员用户"""

    # 初始化配置服务
    config_factory = ConfigServiceFactory()
    config_service = config_factory.create()
    settings = config_service.get_settings()

    # 初始化认证服务
    auth_service = AuthService(settings)
    
    # 获取数据库会话
    async for session in get_async_session():
        user_crud = UserCRUD(session)
        
        # 检查是否已存在管理员用户
        existing_admin = await user_crud.get_by_username("admin")
        if existing_admin:
            print("❌ 管理员用户已存在")
            return
        
        # 创建管理员用户
        admin_password = "admin123"  # 默认密码，建议首次登录后修改
        password_hash = auth_service.get_password_hash(admin_password)
        
        admin_user = User(
            username="admin",
            password_hash=password_hash,
            role="admin",
            is_active=True
        )
        
        # 保存到数据库
        created_user = await user_crud.create(admin_user)
        
        print("✅ 管理员用户创建成功")
        print(f"   用户名: {created_user.username}")
        print(f"   密码: {admin_password}")
        print(f"   角色: {created_user.role}")
        print("   请在首次登录后修改密码")
        
        break


if __name__ == "__main__":
    asyncio.run(create_admin_user())
