import os
import shutil
from pathlib import Path
from typing import Optional
from core.config import settings
from core.crypto import generate_secure_filename


class AvatarService:
    """头像服务"""
    
    @staticmethod
    def ensure_avatar_directory():
        """确保头像目录存在"""
        avatar_dir = Path(settings.avatar_root)
        avatar_dir.mkdir(parents=True, exist_ok=True)
        return avatar_dir
    
    @staticmethod
    def copy_avatar_file(original_uin: int, salt: str) -> str:
        """复制并重命名头像文件"""
        avatar_dir = AvatarService.ensure_avatar_directory()
        
        # 原始文件路径（假设在public/avatars/mems/目录下）
        original_path = Path(f"../public/avatars/mems/{original_uin}.webp")
        
        # 生成安全的文件名
        secure_filename = generate_secure_filename(original_uin, salt)
        target_path = avatar_dir / secure_filename
        
        # 复制文件
        if original_path.exists():
            shutil.copy2(original_path, target_path)
        else:
            # 如果原始文件不存在，创建一个占位符
            target_path.touch()
        
        return secure_filename
    
    @staticmethod
    def get_avatar_path(avatar_hash: str) -> Optional[Path]:
        """获取头像文件路径"""
        avatar_dir = Path(settings.avatar_root)
        avatar_path = avatar_dir / f"{avatar_hash}.webp"
        
        if avatar_path.exists():
            return avatar_path
        
        return None
