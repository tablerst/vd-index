
#!/usr/bin/env python3
"""
QQ群成员数据导入脚本
从JSON文件导入成员数据到PostgreSQL数据库
使用项目的异步数据库架构
"""

import asyncio
import json
import secrets
import sys
from pathlib import Path
from datetime import datetime
from sqlmodel import delete, select

# 修复导入路径
sys.path.append(str(Path(__file__).parent.parent))

from services.database.models.member import Member
from services.database.factory import DatabaseServiceFactory
from services.deps import set_database_service, session_scope
from core.crypto import encrypt_uin, generate_avatar_hash
from core.config import settings


async def import_members(json_path: Path) -> None:
    """
    从JSON文件导入成员数据（异步版本）

    Args:
        json_path: JSON文件路径
    """
    print(f"🔄 开始导入成员数据: {json_path}")

    # 初始化数据库服务
    factory = DatabaseServiceFactory()
    db_service = factory.create(settings.database_url)
    set_database_service(db_service)

    try:
        # 确保数据库表存在
        await db_service.create_db_and_tables()

        # 读取JSON文件
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            print(f"✅ 成功读取JSON文件")
        except Exception as e:
            print(f"❌ 读取JSON文件失败: {e}")
            return

        # 检查JSON结构
        if "mems" not in data:
            print("❌ JSON文件格式错误：缺少 'mems' 字段")
            return

        members_data = data["mems"]
        print(f"📊 找到 {len(members_data)} 个成员")

        # 转换成员数据
        members = []
        for i, item in enumerate(members_data):
            try:
                # 生成随机盐值
                salt = secrets.token_hex(8)  # 8 byte hex = 16 char string

                # 加密UIN
                uin_encrypted = encrypt_uin(item["uin"], salt)

                # 生成头像哈希
                avatar_hash = generate_avatar_hash(item["uin"], salt)

                # 确定显示名称
                display_name = (item.get("card") or item.get("nick") or f"用户{item['uin']}")

                # 转换时间戳
                join_time = datetime.fromtimestamp(item["join_time"])
                last_speak_time = None
                if item.get("last_speak_time"):
                    last_speak_time = datetime.fromtimestamp(item["last_speak_time"])

                # 创建成员对象
                member = Member(
                    display_name=display_name,
                    group_nick=item.get("card") if item.get("card") else None,
                    qq_nick=item.get("nick") if item.get("nick") else None,
                    role=item["role"],
                    uin_encrypted=uin_encrypted,
                    salt=salt,
                    avatar_hash=avatar_hash,
                    join_time=join_time,
                    last_speak_time=last_speak_time,
                    level_point=item.get("lv", {}).get("point", 0),
                    level_value=item.get("lv", {}).get("level", 1),
                    q_age=item.get("qage", 0),
                )

                members.append(member)

            except Exception as e:
                print(f"⚠️  处理第 {i+1} 个成员时出错: {e}")
                continue

        print(f"✅ 成功处理 {len(members)} 个成员数据")

        # 导入到数据库（使用异步会话）
        try:
            async with session_scope() as session:
                # 清空现有数据
                print("🗑️  清空现有成员数据...")
                await session.exec(delete(Member))

                # 批量插入新数据
                print("💾 插入新成员数据...")
                session.add_all(members)
                # session_scope 会自动提交

                print(f"🎉 成功导入 {len(members)} 个成员到数据库")

        except Exception as e:
            print(f"❌ 数据库操作失败: {e}")
            return

    finally:
        # 清理数据库服务
        await db_service.teardown()


async def main():
    """主函数（异步版本）"""
    if len(sys.argv) != 2:
        print("用法: python import_group_json.py <json_file_path>")
        print("示例: python import_group_json.py ../static/qq_group_members.example.json")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"❌ 文件不存在: {json_path}")
        sys.exit(1)

    await import_members(json_path)


if __name__ == "__main__":
    asyncio.run(main())
