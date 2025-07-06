#!/usr/bin/env python3
"""
调试认证系统脚本
检查数据库中的用户信息和密码验证
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from services.deps import get_session
from services.database.models.user import User, UserCRUD
from services.auth.service import AuthService
from services.config.factory import ConfigServiceFactory
from services.database.service import DatabaseService


async def debug_auth():
    """调试认证系统"""
    
    # 初始化配置服务
    config_factory = ConfigServiceFactory()
    config_service = config_factory.create()
    settings = config_service.get_settings()
    
    # 初始化认证服务
    auth_service = AuthService(settings)
    
    # 初始化数据库服务
    db_service = DatabaseService(settings.database_url)
    
    # 获取数据库会话
    async with db_service.with_session() as session:
        user_crud = UserCRUD
        
        print("🔍 调试认证系统...")
        print(f"📋 环境变量配置:")
        print(f"   SUPER_USER_USERNAME: {settings.super_user_username}")
        print(f"   SUPER_USER_PASSWORD: {settings.super_user_password}")
        print()
        
        # 查找admin用户
        admin_user = await user_crud.get_by_username(session, "admin")
        if not admin_user:
            print("❌ 未找到admin用户")
            return
        
        print("✅ 找到admin用户:")
        print(f"   ID: {admin_user.id}")
        print(f"   用户名: {admin_user.username}")
        print(f"   角色: {admin_user.role}")
        print(f"   是否激活: {admin_user.is_active}")
        print(f"   创建时间: {admin_user.created_at}")
        print(f"   密码哈希: {admin_user.password_hash[:50]}...")
        print()
        
        # 测试密码验证
        test_passwords = [
            "Admin9713",  # 当前环境变量中的密码
            "admin123",   # create_admin.py中的默认密码
            "change-this-password-in-production"  # .env.example中的密码
        ]
        
        print("🔐 测试密码验证:")
        for password in test_passwords:
            is_valid = auth_service.verify_password(password, admin_user.password_hash)
            status = "✅ 正确" if is_valid else "❌ 错误"
            print(f"   密码 '{password}': {status}")
        
        print()
        
        # 测试密码哈希生成
        print("🔨 测试密码哈希生成:")
        for password in test_passwords:
            new_hash = auth_service.get_password_hash(password)
            print(f"   密码 '{password}' 的哈希: {new_hash[:50]}...")
            # 验证新生成的哈希
            is_valid = auth_service.verify_password(password, new_hash)
            print(f"   验证结果: {'✅ 正确' if is_valid else '❌ 错误'}")
            print()


if __name__ == "__main__":
    asyncio.run(debug_auth())
