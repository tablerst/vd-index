#!/usr/bin/env python3
"""
后端服务测试脚本
"""
import sys
from pathlib import Path

# 添加app目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.crypto import encrypt_uin, decrypt_uin, generate_avatar_hash


def test_crypto():
    """测试加密解密功能"""
    print("🔐 测试加密解密功能...")
    
    # 测试UIN加密解密
    test_uin = 1234567890
    
    try:
        # 加密
        encrypted = encrypt_uin(test_uin)
        print(f"原始UIN: {test_uin}")
        print(f"加密后: {encrypted}")
        
        # 解密
        decrypted = decrypt_uin(encrypted)
        print(f"解密后: {decrypted}")
        
        # 验证
        if test_uin == decrypted:
            print("✅ 加密解密测试通过")
        else:
            print("❌ 加密解密测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 加密解密测试异常: {e}")
        return False
    
    # 测试头像哈希生成
    try:
        test_id = 123
        avatar_hash = generate_avatar_hash(test_id)
        print(f"代理ID: {test_id}")
        print(f"头像哈希: {avatar_hash}")
        
        if len(avatar_hash) == 64:
            print("✅ 头像哈希生成测试通过")
        else:
            print("❌ 头像哈希长度错误")
            return False
            
    except Exception as e:
        print(f"❌ 头像哈希测试异常: {e}")
        return False
    
    return True


def test_database():
    """测试数据库连接"""
    print("\n📊 测试数据库连接...")
    
    try:
        from app.models import create_db_and_tables, engine
        from sqlmodel import Session, select, func
        from app.models import Member
        
        # 创建数据库和表
        create_db_and_tables()
        print("✅ 数据库表创建成功")
        
        # 测试连接
        with Session(engine) as session:
            count = session.exec(select(func.count(Member.id))).one()
            print(f"✅ 数据库连接成功，当前成员数: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试异常: {e}")
        return False


def test_config():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    try:
        from app.config import settings, get_or_create_aes_key
        
        print(f"数据库URL: {settings.database_url}")
        print(f"头像目录: {settings.avatar_root}")
        print(f"调试模式: {settings.debug}")
        print(f"服务器地址: {settings.host}:{settings.port}")
        
        # 测试密钥生成
        aes_key = get_or_create_aes_key()
        print(f"AES密钥长度: {len(aes_key)} 字符")
        
        print("✅ 配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置测试异常: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始后端服务测试...\n")
    
    tests = [
        ("加密功能", test_crypto),
        ("数据库", test_database),
        ("配置", test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！后端服务准备就绪。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
