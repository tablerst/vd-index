#!/usr/bin/env python3
"""
头像功能调试脚本
用于诊断本地和远程环境的头像获取问题
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings, get_or_create_aes_key
from core.crypto import decrypt_uin, crypto_manager
from services.database.factory import DatabaseServiceFactory
from services.deps import set_database_service


def setup_debug_logging():
    """设置调试日志"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('debug_avatar.log', encoding='utf-8')
        ]
    )


async def debug_environment():
    """调试环境信息"""
    logger = logging.getLogger("DEBUG_ENV")
    
    logger.info("=" * 60)
    logger.info("环境信息调试")
    logger.info("=" * 60)
    
    # 基本环境信息
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"Python路径: {sys.path[:3]}...")
    logger.info(f"调试模式: {settings.debug}")
    
    # 配置信息
    logger.info(f"数据库URL: {settings.database_url}")
    logger.info(f"头像根目录: {settings.avatar_root}")
    logger.info(f"密钥文件路径: {settings.secret_key_file}")
    
    # 检查环境变量
    logger.info(f"UIN_AES_KEY环境变量: {'已设置' if settings.uin_aes_key else '未设置'}")
    if settings.uin_aes_key:
        logger.info(f"环境变量密钥长度: {len(settings.uin_aes_key)}")
    
    # 检查密钥文件
    secret_file = Path(settings.secret_key_file)
    logger.info(f"密钥文件存在: {secret_file.exists()}")
    if secret_file.exists():
        try:
            key_content = secret_file.read_text().strip()
            logger.info(f"密钥文件内容长度: {len(key_content)}")
            logger.info(f"密钥文件前10字符: {key_content[:10]}...")
        except Exception as e:
            logger.error(f"读取密钥文件失败: {e}")
    
    # 检查头像目录
    avatar_dir = Path(settings.avatar_root)
    logger.info(f"头像目录存在: {avatar_dir.exists()}")
    if avatar_dir.exists():
        webp_files = list(avatar_dir.glob("*.webp"))
        logger.info(f"头像文件数量: {len(webp_files)}")
        if len(webp_files) <= 5:
            logger.info(f"头像文件列表: {[f.name for f in webp_files]}")
    else:
        logger.warning(f"头像目录不存在: {avatar_dir}")


async def debug_crypto():
    """调试加密功能"""
    logger = logging.getLogger("DEBUG_CRYPTO")
    
    logger.info("=" * 60)
    logger.info("加密功能调试")
    logger.info("=" * 60)
    
    try:
        # 获取主密钥
        master_key = get_or_create_aes_key()
        logger.info(f"主密钥获取成功，长度: {len(master_key)}")
        logger.info(f"主密钥前10字符: {master_key[:10]}...")
        
        # 测试加密管理器
        logger.info("测试加密管理器初始化...")
        key = crypto_manager.key
        logger.info(f"派生密钥长度: {len(key)}")
        
        # 测试加密解密
        test_uin = 123456789
        test_salt = "test_salt_123"
        
        logger.info(f"测试加密 - UIN: {test_uin}, Salt: {test_salt}")
        encrypted = crypto_manager.encrypt_uin(test_uin, test_salt)
        logger.info(f"加密结果长度: {len(encrypted)}")
        logger.info(f"加密结果前20字符: {encrypted[:20]}...")
        
        logger.info("测试解密...")
        decrypted = crypto_manager.decrypt_uin(encrypted, test_salt)
        logger.info(f"解密结果: {decrypted}")
        
        if decrypted == test_uin:
            logger.info("✅ 加密解密测试成功")
        else:
            logger.error(f"❌ 加密解密测试失败 - 期望: {test_uin}, 实际: {decrypted}")
            
    except Exception as e:
        logger.error(f"❌ 加密功能测试失败: {e}", exc_info=True)


async def debug_database():
    """调试数据库连接和成员数据"""
    logger = logging.getLogger("DEBUG_DB")
    
    logger.info("=" * 60)
    logger.info("数据库调试")
    logger.info("=" * 60)
    
    try:
        # 初始化数据库服务
        factory = DatabaseServiceFactory()
        db_service = factory.create(settings.database_url)
        set_database_service(db_service)
        
        logger.info("数据库服务初始化成功")
        
        # 获取数据库会话
        from services.deps import get_session
        from services.database.models.member import Member
        
        async for session in get_session():
            # 查询成员数量
            from sqlmodel import select
            result = await session.exec(select(Member))
            members = result.all()
            logger.info(f"数据库中的成员数量: {len(members)}")
            
            if members:
                # 测试前几个成员的解密
                test_count = min(3, len(members))
                logger.info(f"测试前{test_count}个成员的解密...")
                
                for i, member in enumerate(members[:test_count]):
                    logger.info(f"成员 {i+1}:")
                    logger.info(f"  ID: {member.id}")
                    logger.info(f"  显示名称: {member.display_name}")
                    logger.info(f"  加密UIN长度: {len(member.uin_encrypted) if member.uin_encrypted else 0}")
                    logger.info(f"  Salt: {member.salt}")
                    
                    try:
                        uin = decrypt_uin(member.uin_encrypted, member.salt)
                        logger.info(f"  解密UIN: {uin}")
                        
                        # 检查对应的头像文件
                        avatar_path = Path(settings.avatar_root) / f"{uin}.webp"
                        logger.info(f"  头像文件路径: {avatar_path}")
                        logger.info(f"  头像文件存在: {avatar_path.exists()}")
                        
                    except Exception as e:
                        logger.error(f"  解密失败: {e}")
            else:
                logger.warning("数据库中没有成员数据")
            
            break  # 只使用第一个会话
            
    except Exception as e:
        logger.error(f"❌ 数据库调试失败: {e}", exc_info=True)


async def main():
    """主函数"""
    setup_debug_logging()
    logger = logging.getLogger("MAIN")
    
    logger.info("开始头像功能调试...")
    
    try:
        await debug_environment()
        await debug_crypto()
        await debug_database()
        
        logger.info("=" * 60)
        logger.info("调试完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"调试过程中发生错误: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
