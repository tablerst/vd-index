"""
Generic upload utilities for static pics
中文注释：通用图片上传保存工具，保存到 ./static/pics/yyyy/mm 目录，并返回相对URL。
"""
from __future__ import annotations

import imghdr
import secrets
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

from fastapi import UploadFile
from io import BytesIO
from PIL import Image

# 允许的MIME前缀（粗略校验）；更严格可结合 Pillow
ALLOWED_IMAGE_MIME_PREFIXES = ("image/",)

# 根静态目录与图片子目录（相对项目根 src/backend/static）
# __file__=src/backend/utils/uploads.py -> parents[1] = src/backend
STATIC_ROOT = Path(__file__).resolve().parents[1] / "static"
PICS_ROOT = STATIC_ROOT / "pics"


def ensure_pics_dir() -> Path:
    """确保 pics 根目录存在"""
    PICS_ROOT.mkdir(parents=True, exist_ok=True)
    return PICS_ROOT


def _safe_ext_from_filename(name: str) -> str:
    """根据原始文件名提取安全扩展名（默认 jpg）"""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else "jpg"
    if ext not in {"jpg", "jpeg", "png", "webp", "gif"}:
        ext = "jpg"
    return ext


def _date_subdir(now: Optional[datetime] = None) -> Path:
    d = now or datetime.utcnow()
    return Path(str(d.year)) / f"{d.month:02d}"


def _gen_filename(ext: str) -> str:
    return f"{secrets.token_hex(8)}.{ext}"


def _guess_image_type(data: bytes) -> Optional[str]:
    """通过 imghdr 简单判断图片类型，返回扩展名（可能返回 None）"""
    kind = imghdr.what(None, h=data)
    if kind == "jpeg":
        return "jpg"
    return kind


async def save_upload_images(images: List[UploadFile]) -> List[Tuple[str, str, Optional[int], Optional[int]]]:
    """保存上传的图片文件到 /static/pics/yyyy/mm
    返回 [(name, url, width, height)] 列表，其中 url 形如 "/static/pics/yyyy/mm/xxxx.jpg"。
    """
    ensure_pics_dir()
    results: List[Tuple[str, str, Optional[int], Optional[int]]] = []
    subdir = _date_subdir()
    target_dir = PICS_ROOT / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    for f in images:
        # 基础MIME检查（仅作为防御，最终以内容判断为准）
        ctype = (f.content_type or "").lower()
        if not any(ctype.startswith(p) for p in ALLOWED_IMAGE_MIME_PREFIXES):
            # 跳过非图片
            await f.read()  # 消费输入流避免资源泄露
            continue
        data = await f.read()
        # 读取尺寸（若失败则为 None）
        width = height = None
        try:
            with Image.open(BytesIO(data)) as img:
                width, height = img.size
        except Exception:
            pass
        # 基于内容或文件名推断扩展名
        ext = _guess_image_type(data) or _safe_ext_from_filename(f.filename or "")
        name = _gen_filename(ext)
        out_path = target_dir / name
        # 写入磁盘
        out_path.write_bytes(data)
        # 构建 URL：统一通过 API 字节流端点返回，避免生产环境静态挂载差异
        url = f"/api/v1/daily/pics/{subdir.as_posix()}/{name}"
        results.append((name, url, width, height))

    return results

