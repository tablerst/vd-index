#!/usr/bin/env python3
"""
数据库初始化脚本
确保数据库和必要的目录结构正确创建
"""
import sys
from pathlib import Path

# 添加app目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.models import create_db_and_tables
from app.config import settings
from app.services import AvatarService


def init_directories():
    """初始化必要的目录"""
    print("📁 创建必要的目录...")
    
    # 创建数据目录
    data_dir = Path("./data")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 数据目录: {data_dir.absolute()}")
    
    # 创建头像目录
    avatar_dir = AvatarService.ensure_avatar_directory()
    print(f"✅ 头像目录: {avatar_dir.absolute()}")
    
    # 创建日志目录
    logs_dir = Path("../logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 日志目录: {logs_dir.absolute()}")


def init_database():
    """初始化数据库"""
    print("🗄️ 初始化数据库...")
    
    try:
        create_db_and_tables()
        print("✅ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


def check_permissions():
    """检查文件权限"""
    print("🔐 检查文件权限...")
    
    # 检查数据目录权限
    data_dir = Path("./data")
    if data_dir.exists():
        if data_dir.is_dir() and data_dir.stat().st_mode & 0o755:
            print("✅ 数据目录权限正常")
        else:
            print("⚠️ 数据目录权限可能有问题")
    
    # 检查密钥文件权限
    secret_file = Path("./secret_key")
    if secret_file.exists():
        if secret_file.stat().st_mode & 0o600:
            print("✅ 密钥文件权限正常")
        else:
            print("⚠️ 密钥文件权限可能有问题")
            try:
                secret_file.chmod(0o600)
                print("✅ 已修复密钥文件权限")
            except Exception as e:
                print(f"❌ 无法修复密钥文件权限: {e}")


def main():
    """主函数"""
    print("🚀 数据库初始化脚本")
    print("=" * 50)
    
    # 显示配置信息
    print(f"📊 配置信息:")
    print(f"   数据库URL: {settings.database_url}")
    print(f"   头像目录: {settings.avatar_root}")
    print(f"   调试模式: {settings.debug}")
    print()
    
    # 初始化目录
    init_directories()
    print()
    
    # 初始化数据库
    success = init_database()
    print()
    
    # 检查权限
    check_permissions()
    print()
    
    if success:
        print("🎉 初始化完成！")
        return True
    else:
        print("❌ 初始化失败！")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
