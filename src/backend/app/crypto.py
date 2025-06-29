"""
加密解密工具模块
"""
import hashlib
import secrets
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from app.config import get_or_create_aes_key


class CryptoManager:
    """加密管理器"""
    
    def __init__(self):
        self._key = None
        self._salt = b"vd_member_salt_2024"  # 固定盐值
    
    @property
    def key(self) -> bytes:
        """获取加密密钥"""
        if self._key is None:
            master_key = get_or_create_aes_key()
            # 使用PBKDF2从主密钥派生AES密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # AES-256需要32字节密钥
                salt=self._salt,
                iterations=100000,
            )
            self._key = kdf.derive(master_key.encode())
        return self._key
    
    def encrypt_uin(self, uin: int) -> str:
        """加密UIN"""
        try:
            aesgcm = AESGCM(self.key)
            nonce = secrets.token_bytes(12)  # GCM推荐12字节nonce
            
            # 将UIN转换为字节
            uin_bytes = str(uin).encode('utf-8')
            
            # 加密
            ciphertext = aesgcm.encrypt(nonce, uin_bytes, None)
            
            # 组合nonce和密文，然后base64编码
            encrypted_data = nonce + ciphertext
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise ValueError(f"UIN加密失败: {e}")
    
    def decrypt_uin(self, encrypted_uin: str) -> int:
        """解密UIN"""
        try:
            aesgcm = AESGCM(self.key)
            
            # base64解码
            encrypted_data = base64.b64decode(encrypted_uin.encode('utf-8'))
            
            # 分离nonce和密文
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            # 解密
            uin_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            
            # 转换回整数
            return int(uin_bytes.decode('utf-8'))
            
        except Exception as e:
            raise ValueError(f"UIN解密失败: {e}")
    
    def generate_avatar_hash(self, surrogate_id: int) -> str:
        """生成头像文件哈希"""
        # 使用代理ID + 盐值生成哈希
        data = f"{surrogate_id}{self._salt.decode()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def generate_secure_filename(self, original_uin: int, surrogate_id: int) -> str:
        """生成安全的文件名"""
        avatar_hash = self.generate_avatar_hash(surrogate_id)
        return f"{avatar_hash}.webp"


# 全局加密管理器实例
crypto_manager = CryptoManager()


def encrypt_uin(uin: int) -> str:
    """加密UIN的便捷函数"""
    return crypto_manager.encrypt_uin(uin)


def decrypt_uin(encrypted_uin: str) -> int:
    """解密UIN的便捷函数"""
    return crypto_manager.decrypt_uin(encrypted_uin)


def generate_avatar_hash(surrogate_id: int) -> str:
    """生成头像哈希的便捷函数"""
    return crypto_manager.generate_avatar_hash(surrogate_id)


def generate_secure_filename(original_uin: int, surrogate_id: int) -> str:
    """生成安全文件名的便捷函数"""
    return crypto_manager.generate_secure_filename(original_uin, surrogate_id)
