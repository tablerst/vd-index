#!/usr/bin/env python3
"""
头像文件复制脚本
将原始头像文件复制到后端安全存储目录，并重命名为安全哈希
"""
import sys
import shutil
from pathlib import Path
from typing import Dict

# 添加app目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.models import Member, engine
from app.crypto import decrypt_uin, generate_avatar_hash


def copy_avatars(source_dir: str, target_dir: str = None):
    """复制头像文件"""
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"❌ 源目录不存在: {source_dir}")
        return False
    
    # 使用默认目标目录
    if target_dir is None:
        target_path = Path("data/avatars")
    else:
        target_path = Path(target_dir)
    
    # 确保目标目录存在
    target_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 源目录: {source_path}")
    print(f"📁 目标目录: {target_path}")
    
    # 从数据库获取所有成员
    with Session(engine) as session:
        members = session.exec(select(Member)).all()
        print(f"📊 数据库中共有 {len(members)} 个成员")
    
    copied_count = 0
    failed_count = 0
    
    for member in members:
        try:
            # 解密UIN
            original_uin = decrypt_uin(member.uin_encrypted)
            
            # 查找源文件
            source_file = source_path / f"{original_uin}.webp"
            if not source_file.exists():
                # 尝试其他格式
                for ext in ['.jpg', '.jpeg', '.png']:
                    alt_source = source_path / f"{original_uin}{ext}"
                    if alt_source.exists():
                        source_file = alt_source
                        break
            
            if source_file.exists():
                # 生成目标文件名（使用成员的avatar_hash）
                target_filename = f"{member.avatar_hash}.webp"
                target_file = target_path / target_filename
                
                # 复制文件
                shutil.copy2(source_file, target_file)
                copied_count += 1
                print(f"✅ 复制: {original_uin} -> {member.avatar_hash}")
            else:
                failed_count += 1
                print(f"❌ 文件不存在: {original_uin}")
                
        except Exception as e:
            failed_count += 1
            print(f"❌ 处理失败 ID {member.id}: {e}")
    
    print(f"\n📈 复制完成:")
    print(f"  ✅ 成功: {copied_count} 个")
    print(f"  ❌ 失败: {failed_count} 个")
    
    return copied_count > 0


def verify_avatars(target_dir: str = None):
    """验证头像文件"""
    if target_dir is None:
        target_path = Path("data/avatars")
    else:
        target_path = Path(target_dir)
    
    if not target_path.exists():
        print(f"❌ 目标目录不存在: {target_path}")
        return False
    
    # 从数据库获取所有成员
    with Session(engine) as session:
        members = session.exec(select(Member)).all()
    
    existing_count = 0
    missing_count = 0
    
    print(f"🔍 验证头像文件...")
    
    for member in members:
        avatar_file = target_path / f"{member.avatar_hash}.webp"
        if avatar_file.exists():
            existing_count += 1
            file_size = avatar_file.stat().st_size
            print(f"✅ {member.display_name}: {member.avatar_hash}.webp ({file_size} bytes)")
        else:
            missing_count += 1
            print(f"❌ {member.display_name}: {member.avatar_hash}.webp (缺失)")
    
    print(f"\n📊 验证结果:")
    print(f"  ✅ 存在: {existing_count} 个")
    print(f"  ❌ 缺失: {missing_count} 个")
    
    return missing_count == 0


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python copy_avatars.py <source_dir> [target_dir]")
        print("示例: python copy_avatars.py ../public/avatars/mems")
        print("      python copy_avatars.py ../public/avatars/mems ./data/avatars")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    target_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("🚀 开始复制头像文件...")
    
    # 复制头像
    success = copy_avatars(source_dir, target_dir)
    
    if success:
        print("\n🔍 验证复制结果...")
        verify_avatars(target_dir)
        print("\n🎉 头像复制完成！")
    else:
        print("\n❌ 头像复制失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
