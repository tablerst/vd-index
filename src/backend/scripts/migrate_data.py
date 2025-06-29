#!/usr/bin/env python3
"""
数据迁移脚本
从前端的JSON文件迁移数据到后端数据库
"""
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加app目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session
from app.models import Member, engine, create_db_and_tables
from app.crypto import encrypt_uin, generate_avatar_hash
from app.services import AvatarService


def load_json_data(json_file_path: str) -> Dict[str, Any]:
    """加载JSON数据文件"""
    json_path = Path(json_file_path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON文件不存在: {json_file_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def migrate_member_data(json_data: Dict[str, Any]) -> List[Member]:
    """迁移成员数据"""
    if 'mems' not in json_data:
        raise ValueError("JSON数据格式错误，缺少mems字段")
    
    members = []
    
    for mem_data in json_data['mems']:
        try:
            # 提取基本信息
            uin = mem_data['uin']
            role = mem_data['role']
            join_time = datetime.fromtimestamp(mem_data['join_time'])
            last_speak_time = None
            if mem_data.get('last_speak_time'):
                last_speak_time = datetime.fromtimestamp(mem_data['last_speak_time'])
            
            card = mem_data.get('card', '').strip()
            nick = mem_data.get('nick', '').strip()
            
            # 确定显示名称
            display_name = card or nick
            if not display_name:
                display_name = f"用户{uin}"
            
            # 等级信息
            lv_info = mem_data.get('lv', {})
            level_point = lv_info.get('point', 0)
            level_value = lv_info.get('level', 1)
            
            # Q龄
            q_age = mem_data.get('qage', 0)
            
            # 加密UIN
            encrypted_uin = encrypt_uin(uin)
            
            # 创建成员对象（暂时不设置avatar_hash）
            member = Member(
                display_name=display_name,
                group_nick=card if card else None,
                qq_nick=nick if nick else None,
                uin_encrypted=encrypted_uin,
                avatar_hash="",  # 稍后设置
                role=role,
                join_time=join_time,
                last_speak_time=last_speak_time,
                level_point=level_point,
                level_value=level_value,
                q_age=q_age
            )
            
            # 临时存储原始UIN用于后续处理
            member._original_uin = uin
            
            members.append(member)
            
        except Exception as e:
            print(f"处理成员数据失败 UIN {mem_data.get('uin', 'unknown')}: {e}")
            continue
    
    return members


def copy_avatar_files(members: List[Member], avatar_source_dir: str):
    """复制头像文件"""
    source_dir = Path(avatar_source_dir)
    if not source_dir.exists():
        print(f"警告: 头像源目录不存在: {avatar_source_dir}")
        return
    
    # 确保目标目录存在
    AvatarService.ensure_avatar_directory()
    target_dir = Path(AvatarService.ensure_avatar_directory())
    
    copied_count = 0
    failed_count = 0
    
    for member in members:
        try:
            original_uin = member._original_uin
            
            # 查找源文件
            source_file = source_dir / f"{original_uin}.webp"
            if not source_file.exists():
                # 尝试其他格式
                for ext in ['.jpg', '.jpeg', '.png']:
                    alt_source = source_dir / f"{original_uin}{ext}"
                    if alt_source.exists():
                        source_file = alt_source
                        break
            
            if source_file.exists():
                # 生成目标文件名
                target_filename = f"{member.avatar_hash}.webp"
                target_file = target_dir / target_filename
                
                # 复制文件
                shutil.copy2(source_file, target_file)
                copied_count += 1
                print(f"复制头像: {original_uin} -> {member.avatar_hash}")
            else:
                failed_count += 1
                print(f"头像文件不存在: {original_uin}")
                
        except Exception as e:
            failed_count += 1
            print(f"复制头像失败 UIN {getattr(member, '_original_uin', 'unknown')}: {e}")
    
    print(f"头像复制完成: 成功 {copied_count} 个，失败 {failed_count} 个")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python migrate_data.py <json_file_path> [avatar_source_dir]")
        print("示例: python migrate_data.py ../public/qq_group_937303337_members.json ../public/avatars/mems")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    avatar_source_dir = sys.argv[2] if len(sys.argv) > 2 else "../public/avatars/mems"
    
    try:
        print("🚀 开始数据迁移...")
        
        # 创建数据库和表
        print("📊 初始化数据库...")
        create_db_and_tables()
        
        # 加载JSON数据
        print(f"📁 加载JSON数据: {json_file_path}")
        json_data = load_json_data(json_file_path)
        
        # 迁移成员数据
        print("👥 迁移成员数据...")
        members = migrate_member_data(json_data)
        print(f"解析到 {len(members)} 个成员")
        
        # 保存到数据库
        print("💾 保存到数据库...")
        with Session(engine) as session:
            for member in members:
                session.add(member)
            session.commit()
            
            # 刷新获取ID并设置avatar_hash
            for member in members:
                session.refresh(member)
                member.avatar_hash = generate_avatar_hash(member.id)
                session.add(member)
            session.commit()
        
        print(f"✅ 成功保存 {len(members)} 个成员到数据库")
        
        # 复制头像文件
        print("🖼️ 复制头像文件...")
        copy_avatar_files(members, avatar_source_dir)
        
        print("🎉 数据迁移完成！")
        
        # 显示统计信息
        with Session(engine) as session:
            from sqlmodel import select, func
            total_count = session.exec(select(func.count(Member.id))).one()
            print(f"📈 数据库中共有 {total_count} 个成员")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
