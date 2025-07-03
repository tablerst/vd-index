#!/usr/bin/env python3
"""
复制头像文件脚本
将前端的头像文件复制到后端静态目录
"""
import shutil
from pathlib import Path


def copy_avatars():
    """复制头像文件"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent

    # 源目录（前端）
    source_dir = script_dir / "../../frontend/public/avatars/mems"

    # 目标目录（后端）
    target_dir = script_dir / "../static/avatars/mems"

    print(f"源目录: {source_dir.resolve()}")
    print(f"目标目录: {target_dir.resolve()}")
    print(f"源目录存在: {source_dir.exists()}")
    print(f"目标目录存在: {target_dir.exists()}")
    
    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    if not source_dir.exists():
        print(f"错误: 源目录不存在: {source_dir}")
        return

    # 复制所有webp文件
    copied_count = 0
    for avatar_file in source_dir.glob("*.webp"):
        target_file = target_dir / avatar_file.name
        shutil.copy2(avatar_file, target_file)
        copied_count += 1
        print(f"复制: {avatar_file.name}")

    print(f"\n总共复制了 {copied_count} 个头像文件")


if __name__ == "__main__":
    copy_avatars()
