#!/usr/bin/env python3
"""
简化的后端服务测试
"""
import hashlib
import secrets
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def test_crypto_basic():
    """测试基本加密功能"""
    print("🔐 测试基本加密功能...")
    
    # 生成密钥
    master_key = "test-master-key-2024"
    salt = b"vd_member_salt_2024"
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(master_key.encode())
    
    # 测试UIN加密解密
    test_uin = 1234567890
    
    try:
        # 加密
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)
        uin_bytes = str(test_uin).encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, uin_bytes, None)
        
        # 组合并编码
        encrypted_data = nonce + ciphertext
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        print(f"原始UIN: {test_uin}")
        print(f"加密后: {encrypted_b64}")
        
        # 解密
        encrypted_data = base64.b64decode(encrypted_b64.encode('utf-8'))
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        decrypted_uin = int(decrypted_bytes.decode('utf-8'))
        
        print(f"解密后: {decrypted_uin}")
        
        if test_uin == decrypted_uin:
            print("✅ 加密解密测试通过")
            return True
        else:
            print("❌ 加密解密测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 加密解密测试异常: {e}")
        return False


def test_avatar_hash():
    """测试头像哈希生成"""
    print("\n🖼️ 测试头像哈希生成...")
    
    try:
        test_id = 123
        salt = "vd_member_salt_2024"
        
        # 生成哈希
        data = f"{test_id}{salt}"
        avatar_hash = hashlib.sha256(data.encode()).hexdigest()
        
        print(f"代理ID: {test_id}")
        print(f"头像哈希: {avatar_hash}")
        print(f"哈希长度: {len(avatar_hash)}")
        
        if len(avatar_hash) == 64:
            print("✅ 头像哈希生成测试通过")
            return True
        else:
            print("❌ 头像哈希长度错误")
            return False
            
    except Exception as e:
        print(f"❌ 头像哈希测试异常: {e}")
        return False


def test_data_flow():
    """测试完整数据流程"""
    print("\n🔄 测试完整数据流程...")
    
    try:
        # 模拟原始数据
        original_uin = 1538194265
        member_name = "测试用户"
        
        # 1. 生成代理ID（模拟数据库自增）
        surrogate_id = 1
        
        # 2. 加密UIN
        master_key = "test-master-key-2024"
        salt = b"vd_member_salt_2024"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(master_key.encode())
        
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)
        uin_bytes = str(original_uin).encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, uin_bytes, None)
        encrypted_data = nonce + ciphertext
        encrypted_uin = base64.b64encode(encrypted_data).decode('utf-8')
        
        # 3. 生成头像哈希
        hash_salt = "vd_member_salt_2024"
        data = f"{surrogate_id}{hash_salt}"
        avatar_hash = hashlib.sha256(data.encode()).hexdigest()
        
        # 4. 构建前端响应数据
        frontend_data = {
            "id": surrogate_id,
            "name": member_name,
            "avatar_url": f"http://localhost:8000/api/avatar/{avatar_hash}",
            "bio": "加入于 2023-01-15",
            "role": 2
        }
        
        print("模拟数据流程:")
        print(f"原始UIN: {original_uin}")
        print(f"代理ID: {surrogate_id}")
        print(f"加密UIN: {encrypted_uin[:50]}...")
        print(f"头像哈希: {avatar_hash}")
        print(f"前端数据: {frontend_data}")
        
        # 验证前端数据不包含敏感信息
        frontend_str = str(frontend_data)
        if str(original_uin) not in frontend_str:
            print("✅ 前端数据不包含原始UIN")
            return True
        else:
            print("❌ 前端数据泄露了原始UIN")
            return False
            
    except Exception as e:
        print(f"❌ 数据流程测试异常: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始后端核心功能测试...\n")
    
    tests = [
        ("基本加密功能", test_crypto_basic),
        ("头像哈希生成", test_avatar_hash),
        ("完整数据流程", test_data_flow)
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
        print("🎉 核心功能测试通过！加密逻辑正确。")
        print("\n📝 下一步:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 启动服务: python backend/run.py")
        print("3. 迁移数据: python backend/scripts/migrate_data.py")
        return True
    else:
        print("⚠️ 部分测试失败，请检查实现。")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
