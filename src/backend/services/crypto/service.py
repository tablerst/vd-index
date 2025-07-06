"""
加密解密服务模块
"""
import hashlib
import secrets
import logging
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# 设置日志记录器
logger = logging.getLogger(__name__)


class CryptoService:
    """加密服务类"""
    
    name = "crypto_service"
    
    def __init__(self, config_service):
        """初始化加密服务
        
        Args:
            config_service: 配置服务实例
        """
        self.config_service = config_service
        self._key = None
        self._salt = b"vd_member_salt_2024"  # 固定盐值
    
    @property
    def key(self) -> bytes:
        """获取加密密钥"""
        if self._key is None:
            logger.debug("[CRYPTO] 初始化加密密钥")
            master_key = self.config_service.get_or_create_aes_key()
            logger.debug(f"[CRYPTO] 主密钥长度: {len(master_key)}")
            logger.debug(f"[CRYPTO] 主密钥前10字符: {master_key[:10]}...")

            # 使用PBKDF2从主密钥派生AES密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # AES-256需要32字节密钥
                salt=self._salt,
                iterations=100000,
            )
            self._key = kdf.derive(master_key.encode())
            logger.debug(f"[CRYPTO] 派生密钥长度: {len(self._key)}")
            logger.info("[CRYPTO] 加密密钥初始化完成")
        return self._key
    
    def encrypt_uin(self, uin: int, salt: str) -> str:
        """加密UIN"""
        try:
            aesgcm = AESGCM(self.key)
            nonce = secrets.token_bytes(12)
            mixed = f"{uin}vd{salt}".encode("utf-8")
            cipher = aesgcm.encrypt(nonce, mixed, None)
            return base64.b64encode(nonce + cipher).decode()
            
        except Exception as e:
            raise ValueError(f"UIN加密失败: {e}")
    
    def decrypt_uin(self, encrypted_uin: str, salt: str) -> int:
        """解密UIN"""
        logger.debug(f"[CRYPTO] 开始解密UIN - salt: {salt}")
        logger.debug(f"[CRYPTO] 加密数据长度: {len(encrypted_uin) if encrypted_uin else 0}")
        logger.debug(f"[CRYPTO] 加密数据前20字符: {encrypted_uin[:20] if encrypted_uin and len(encrypted_uin) > 20 else encrypted_uin}")

        try:
            if not encrypted_uin:
                raise ValueError("加密UIN为空")

            if not salt:
                raise ValueError("Salt为空")

            aesgcm = AESGCM(self.key)
            logger.debug("[CRYPTO] AESGCM实例创建成功")

            # base64解码
            try:
                encrypted_data = base64.b64decode(encrypted_uin.encode('utf-8'))
                logger.debug(f"[CRYPTO] Base64解码成功，数据长度: {len(encrypted_data)}")
            except Exception as e:
                raise ValueError(f"Base64解码失败: {e}")

            # 分离nonce和密文
            if len(encrypted_data) < 12:
                raise ValueError(f"加密数据长度不足，期望至少12字节，实际: {len(encrypted_data)}")

            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            logger.debug(f"[CRYPTO] Nonce长度: {len(nonce)}, 密文长度: {len(ciphertext)}")

            # 解密
            try:
                mixed_bytes = aesgcm.decrypt(nonce, ciphertext, None)
                logger.debug(f"[CRYPTO] AES解密成功，解密数据长度: {len(mixed_bytes)}")
            except Exception as e:
                raise ValueError(f"AES解密失败: {e}")

            try:
                mixed_str = mixed_bytes.decode('utf-8')
                logger.debug(f"[CRYPTO] UTF-8解码成功，混合字符串: {mixed_str}")
            except Exception as e:
                raise ValueError(f"UTF-8解码失败: {e}")

            # 解析出uin
            expected_suffix = f"vd{salt}"
            logger.debug(f"[CRYPTO] 期望的后缀: {expected_suffix}")

            if not mixed_str.endswith(expected_suffix):
                raise ValueError(f"混合字符串格式错误，期望以'{expected_suffix}'结尾，实际: '{mixed_str}'")

            uin_str = mixed_str.replace(expected_suffix, "")
            logger.debug(f"[CRYPTO] 提取的UIN字符串: {uin_str}")

            try:
                uin = int(uin_str)
                logger.info(f"[CRYPTO] UIN解密成功: {uin}")
                return uin
            except ValueError as e:
                raise ValueError(f"UIN字符串转换为整数失败: {e}")

        except Exception as e:
            logger.error(f"[CRYPTO] UIN解密失败 - salt: {salt}, error: {str(e)}", exc_info=True)
            raise ValueError(f"UIN解密失败: {e}")
    
    def generate_avatar_hash(self, uin: int, salt: str) -> str:
        """生成头像文件哈希"""
        # 使用 UIN + 盐值生成哈希
        data = f"{uin}vd{salt}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def generate_secure_filename(self, uin: int, salt: str) -> str:
        """生成安全的文件名"""
        avatar_hash = self.generate_avatar_hash(uin, salt)
        return f"{avatar_hash}.webp"
