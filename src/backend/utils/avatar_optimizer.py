"""
批量将 avatars 目录下头像资源转换为 WebP/AVIF 或重新压缩 JPEG，
并打包到 /avatars/zip 目录下。
"""

import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Iterable

from PIL import Image  # Pillow>=10.0 已支持 AVIF
# ↓ 新增：动态导入 pillow-avif-plugin（或其他兼容插件）
try:
    import pillow_avif  # noqa: F401  # 安装包：pip install pillow-avif-plugin
    AVIF_SUPPORTED = True
except ImportError:
    AVIF_SUPPORTED = False
    print("[WARN] 未检测到 AVIF 编码器，已跳过 AVIF 输出")

# ---------------- 常量配置 ---------------- #
INPUT_DIR = Path("avatars") / "937303337_140"             # 原始头像目录
OUTPUT_DIR = INPUT_DIR / "optimized"    # 转换后文件临时目录
ZIP_DIR = INPUT_DIR / "zip"             # zip 输出目录
ZIP_NAME = f"avatars_{int(time.time())}.zip"

# 需生成的目标格式，可选 "webp" / "avif" / "jpeg"
# TARGET_FORMATS: Iterable[str] = ("webp", "avif")  # 只生成这里列出的格式，如需 JPEG 请加 "jpeg"
TARGET_FORMATS: Iterable[str] = ("webp", )  # 只生成这里列出的格式，如需 JPEG 请加 "jpeg"

# WebP/AVIF 压缩质量 (0-100)。如需无损，可设定 lossless=True
QUALITY = 80
JPEG_QUALITY = 85          # 仅当 "jpeg" 在 TARGET_FORMATS 时生效
# 支持的输入扩展名
SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".avif")
# ----------------------------------------- #


def convert_image(src: Path):
    """按配置转换单张图片."""
    try:
        img = Image.open(src)
    except Exception as e:
        print(f"[WARN] 打开失败 {src}: {e}")
        return

    basename = src.stem

    for fmt in TARGET_FORMATS:
        if fmt == "avif" and not AVIF_SUPPORTED:
            continue

        # ---- 根据格式决定输出文件名和保存参数 ----
        if fmt in ("jpeg", "jpg"):
            dst = OUTPUT_DIR / f"{basename}.jpg"
            save_params = dict(quality=JPEG_QUALITY, optimize=True, progressive=True)
            pil_format = "JPEG"
        elif fmt == "webp":
            dst = OUTPUT_DIR / f"{basename}.webp"
            save_params = dict(quality=QUALITY, optimize=True, method=6)
            pil_format = "WEBP"
        elif fmt == "avif":
            dst = OUTPUT_DIR / f"{basename}.avif"
            save_params = dict(quality=QUALITY, optimize=True, speed=5)
            pil_format = "AVIF"
        else:
            continue  # 未知格式，跳过

        try:
            img.save(dst, pil_format, **save_params)
            print(f"   {pil_format:4} ✔  {dst.name}")
        except OSError as e:
            print(f"[WARN] {pil_format} 失败 {src}: {e}")


def main():
    if not INPUT_DIR.exists():
        print(f"[ERROR] 输入目录不存在: {INPUT_DIR.resolve()}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ZIP_DIR.mkdir(parents=True, exist_ok=True)

    images = [p for p in INPUT_DIR.iterdir() if p.suffix.lower() in SUPPORTED_EXTS and p.is_file()]

    if not images:
        print("[INFO] 未找到待处理文件")
        return

    print(f"[INFO] 开始处理 {len(images)} 张图片 ...")
    for img_path in images:
        print(f"[INFO] {img_path.name}")
        convert_image(img_path)

    # 打包 zip
    zip_path = ZIP_DIR / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for file in OUTPUT_DIR.iterdir():
            zf.write(file, arcname=file.name)
    print(f"[INFO] 已生成压缩包: {zip_path.resolve()}")


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
