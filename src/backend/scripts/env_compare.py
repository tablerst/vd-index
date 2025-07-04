#!/usr/bin/env python3
"""
环境对比脚本
用于对比本地和远程环境的配置差异
"""
import os
import sys
import hashlib
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings


def get_file_hash(file_path):
    """获取文件的MD5哈希值"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        return f"ERROR: {e}"


def check_environment():
    """检查环境信息"""
    print("=" * 60)
    print("环境信息对比")
    print("=" * 60)
    
    # 基本环境
    print("基本环境:")
    print(f"  操作系统: {os.name}")
    print(f"  当前目录: {os.getcwd()}")
    print(f"  Python版本: {sys.version}")
    print()
    
    # 环境变量
    print("关键环境变量:")
    env_vars = [
        'DATABASE_URL', 'AVATAR_ROOT', 'UIN_AES_KEY', 'SECRET_KEY_FILE',
        'HOST', 'PORT', 'DEBUG', 'ALLOWED_ORIGINS', 'ALLOWED_HOSTS'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "未设置")
        if var == 'UIN_AES_KEY' and value != "未设置":
            # 隐藏敏感信息
            value = f"已设置(长度:{len(value)})"
        print(f"  {var}: {value}")
    print()
    
    # 配置文件
    print("配置信息:")
    print(f"  数据库URL: {settings.database_url}")
    print(f"  头像根目录: {settings.avatar_root}")
    print(f"  密钥文件路径: {settings.secret_key_file}")
    print(f"  调试模式: {settings.debug}")
    print(f"  主机: {settings.host}")
    print(f"  端口: {settings.port}")
    print()
    
    # 文件检查
    print("关键文件检查:")
    
    # .env文件
    env_file = Path(".env")
    print(f"  .env文件存在: {env_file.exists()}")
    if env_file.exists():
        print(f"  .env文件大小: {env_file.stat().st_size} bytes")
        print(f"  .env文件哈希: {get_file_hash(env_file)}")
    
    # 密钥文件
    secret_file = Path(settings.secret_key_file)
    print(f"  密钥文件存在: {secret_file.exists()}")
    if secret_file.exists():
        print(f"  密钥文件大小: {secret_file.stat().st_size} bytes")
        print(f"  密钥文件哈希: {get_file_hash(secret_file)}")
        try:
            content = secret_file.read_text().strip()
            print(f"  密钥内容长度: {len(content)}")
            print(f"  密钥前10字符: {content[:10]}...")
        except Exception as e:
            print(f"  读取密钥失败: {e}")
    
    # 头像目录
    avatar_dir = Path(settings.avatar_root)
    print(f"  头像目录存在: {avatar_dir.exists()}")
    if avatar_dir.exists():
        webp_files = list(avatar_dir.glob("*.webp"))
        print(f"  头像文件数量: {len(webp_files)}")
        if webp_files:
            total_size = sum(f.stat().st_size for f in webp_files)
            print(f"  头像文件总大小: {total_size} bytes")
            # 显示前几个文件的信息
            for i, f in enumerate(webp_files[:3]):
                print(f"    {f.name}: {f.stat().st_size} bytes")
            if len(webp_files) > 3:
                print(f"    ... 还有 {len(webp_files) - 3} 个文件")
    print()
    
    # 数据库文件（如果是SQLite）
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        db_file = Path(db_path)
        print(f"数据库文件检查:")
        print(f"  数据库文件存在: {db_file.exists()}")
        if db_file.exists():
            print(f"  数据库文件大小: {db_file.stat().st_size} bytes")
            print(f"  数据库文件哈希: {get_file_hash(db_file)}")
    print()
    
    # 权限检查
    print("权限检查:")
    try:
        # 检查当前目录写权限
        test_file = Path("test_write_permission.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print("  当前目录写权限: ✅")
    except Exception as e:
        print(f"  当前目录写权限: ❌ {e}")
    
    try:
        # 检查头像目录读权限
        if avatar_dir.exists():
            list(avatar_dir.iterdir())
            print("  头像目录读权限: ✅")
        else:
            print("  头像目录读权限: ❌ 目录不存在")
    except Exception as e:
        print(f"  头像目录读权限: ❌ {e}")
    
    print()
    print("=" * 60)
    print("检查完成")
    print("=" * 60)
    print()
    print("使用说明:")
    print("1. 在本地环境运行此脚本，保存输出结果")
    print("2. 在远程环境运行此脚本，保存输出结果")
    print("3. 对比两个输出结果，找出差异")
    print("4. 重点关注:")
    print("   - 密钥文件的存在性和内容")
    print("   - 头像目录的存在性和文件数量")
    print("   - 环境变量的设置")
    print("   - 文件权限问题")


if __name__ == "__main__":
    check_environment()
