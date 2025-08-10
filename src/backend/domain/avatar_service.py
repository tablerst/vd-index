"""
头像业务逻辑服务
"""
import os
import shutil
from io import BytesIO
from pathlib import Path
from typing import Optional, List, Dict

import httpx
from PIL import Image

from services.deps import get_config_service, get_crypto_service


class AvatarService:
    """头像服务"""

    @staticmethod
    def ensure_avatar_directory() -> Path:
        """确保头像目录存在"""
        config_service = get_config_service()
        settings = config_service.get_settings()
        avatar_dir = Path(settings.avatar_root)
        avatar_dir.mkdir(parents=True, exist_ok=True)
        return avatar_dir

    @staticmethod
    def copy_avatar_file(original_uin: int, salt: str) -> str:
        """复制并重命名头像文件
        注意：当前系统头像访问使用 uin.webp，保留此方法以兼容旧逻辑。
        """
        avatar_dir = AvatarService.ensure_avatar_directory()

        # 原始文件路径（假设在public/avatars/mems/目录下）
        original_path = Path(f"../public/avatars/mems/{original_uin}.webp")

        # 生成安全的文件名
        crypto_service = get_crypto_service()
        secure_filename = crypto_service.generate_secure_filename(original_uin, salt)
        target_path = avatar_dir / secure_filename

        # 复制文件
        if original_path.exists():
            shutil.copy2(original_path, target_path)
        else:
            # 如果原始文件不存在，创建一个占位符
            target_path.touch()

        return secure_filename

    @staticmethod
    def get_avatar_path_by_uin(uin: int) -> Optional[Path]:
        """根据 UIN 获取头像路径 (uin.webp)"""
        settings = get_config_service().get_settings()
        avatar_path = Path(settings.avatar_root) / f"{uin}.webp"
        return avatar_path if avatar_path.exists() else None

    @staticmethod
    def get_avatar_path(avatar_hash: str) -> Optional[Path]:
        """获取头像文件路径 (兼容旧接口: 以哈希命名)"""
        settings = get_config_service().get_settings()
        avatar_dir = Path(settings.avatar_root)
        avatar_path = avatar_dir / f"{avatar_hash}.webp"
        return avatar_path if avatar_path.exists() else None

    # ---------------- 新增：QQ头像下载与WebP转换 ---------------- #

    @staticmethod
    async def fetch_and_save_avatar_webp(uin: int, size: str = "640", timeout_s: float = 20.0) -> bool:
        """下载 QQ 头像并以 WebP 格式保存为 {avatar_root}/{uin}.webp
        - 使用 httpx 异步请求
        - 使用 Pillow 转换为 WebP
        """
        avatar_dir = AvatarService.ensure_avatar_directory()
        url = f"https://q.qlogo.cn/g?b=qq&nk={uin}&s={size}"
        try:
            async with httpx.AsyncClient(timeout=timeout_s, headers={"User-Agent": "Apifox/1.0.0 (https://apifox.com)"}) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                content_type = (resp.headers.get("content-type") or "").lower()
                if "image" not in content_type:
                    return False
                data = resp.content
            # 使用 Pillow 从内存中打开并转换为 WebP
            with Image.open(BytesIO(data)) as img:
                if img.mode in ("P", "RGBA", "LA"):
                    img = img.convert("RGB")
                out_path = avatar_dir / f"{uin}.webp"
                img.save(out_path, format="WEBP", quality=80, method=6)
            return True
        except Exception:
            return False

    @staticmethod
    async def batch_fetch_and_save_avatars_webp(uins: List[int], size: str = "640") -> Dict[str, int]:
        """批量下载并保存头像为 WebP。返回统计信息。"""
        success = failed = 0
        # 去重
        seen = set()
        for u in uins:
            if not u or u in seen:
                continue
            seen.add(u)
            ok = await AvatarService.fetch_and_save_avatar_webp(u, size=size)
            if ok:
                success += 1
            else:
                failed += 1
        return {"success": success, "failed": failed, "total": len(seen)}

    @staticmethod
    def delete_avatar_file_by_uin(uin: int) -> bool:
        """删除 {avatar_root}/{uin}.webp 头像文件（如果存在）"""
        settings = get_config_service().get_settings()
        p = Path(settings.avatar_root) / f"{uin}.webp"
        try:
            if p.exists():
                p.unlink(missing_ok=True)
                return True
            return False
        except Exception:
            # 删除失败不应阻塞主流程
            return False
