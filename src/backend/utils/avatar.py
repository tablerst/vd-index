"""
Avatar utilities
中文注释：头像相关的工具方法，原 domain.avatar_service 迁移至此，避免放在领域服务层。
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional, List, Dict

import httpx
from PIL import Image

from services.deps import get_config_service, get_crypto_service


class AvatarService:
    """Avatar utility service"""

    @staticmethod
    def ensure_avatar_directory() -> Path:
        """Ensure avatar directory exists"""
        config_service = get_config_service()
        settings = config_service.get_settings()
        avatar_dir = Path(settings.avatar_root)
        avatar_dir.mkdir(parents=True, exist_ok=True)
        return avatar_dir

    @staticmethod
    def get_avatar_path_by_uin(uin: int) -> Optional[Path]:
        """Get avatar path by UIN: {avatar_root}/{uin}.webp"""
        settings = get_config_service().get_settings()
        avatar_path = Path(settings.avatar_root) / f"{uin}.webp"
        return avatar_path if avatar_path.exists() else None

    @staticmethod
    def get_avatar_path(avatar_hash: str) -> Optional[Path]:
        """Get avatar path by hash (legacy compatibility)"""
        settings = get_config_service().get_settings()
        avatar_dir = Path(settings.avatar_root)
        avatar_path = avatar_dir / f"{avatar_hash}.webp"
        return avatar_path if avatar_path.exists() else None

    @staticmethod
    async def fetch_and_save_avatar_webp(uin: int, size: str = "640", timeout_s: float = 20.0) -> bool:
        """Download QQ avatar and save as WebP {avatar_root}/{uin}.webp"""
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
            # Convert to WebP using Pillow
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
        """Batch download and save avatars as WebP. Return stats."""
        success = failed = 0
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
        """Delete {avatar_root}/{uin}.webp if exists"""
        settings = get_config_service().get_settings()
        p = Path(settings.avatar_root) / f"{uin}.webp"
        try:
            if p.exists():
                p.unlink(missing_ok=True)
                return True
            return False
        except Exception:
            # Do not block main flow on delete failure
            return False

