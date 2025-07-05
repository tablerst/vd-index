#!/usr/bin/env python3
"""
创建示例活动数据脚本
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import random

# 添加项目根目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.database.factory import DatabaseServiceFactory
from services.database.models.activity import ActivityCRUD, ActivityCreate
from services.database.models.member import MemberCRUD
from services.deps import set_database_service
from core.config import settings


# 示例活动数据
SAMPLE_ACTIVITIES = [
    {
        "title": "VRC Division成立",
        "description": "一个充满温暖与创造力的社区正式诞生，开启了我们共同的美好旅程。",
        "date": datetime(2023, 1, 15),
        "tags": ["里程碑", "社区"],
        "participant_count": 8
    },
    {
        "title": "首届技术分享会",
        "description": "成员们分享各自的技术心得，促进知识交流与学习成长。",
        "date": datetime(2023, 3, 20),
        "tags": ["技术", "分享"],
        "participant_count": 12
    },
    {
        "title": "春季户外活动",
        "description": "走出室内，拥抱自然，增进成员间的友谊与团队凝聚力。",
        "date": datetime(2023, 4, 10),
        "tags": ["户外", "团建"],
        "participant_count": 15
    },
    {
        "title": "创意设计大赛",
        "description": "发挥创意，展示设计才华，为社区带来更多美好的视觉体验。",
        "date": datetime(2023, 6, 15),
        "tags": ["设计", "比赛"],
        "participant_count": 6
    },
    {
        "title": "夏日音乐节",
        "description": "音乐无界限，让美妙的旋律连接每一颗心，共度美好夏日时光。",
        "date": datetime(2023, 7, 22),
        "tags": ["音乐", "娱乐"],
        "participant_count": 10
    },
    {
        "title": "秋季编程马拉松",
        "description": "48小时不间断编程挑战，激发创新思维，打造优秀作品。",
        "date": datetime(2023, 9, 16),
        "tags": ["编程", "挑战"],
        "participant_count": 18
    },
    {
        "title": "年终总结大会",
        "description": "回顾一年的成长历程，展望未来的发展方向，共同规划新的目标。",
        "date": datetime(2023, 12, 30),
        "tags": ["总结", "规划"],
        "participant_count": 25
    },
    {
        "title": "新春联欢会",
        "description": "欢聚一堂庆新春，分享快乐与温暖，增进彼此的友谊。",
        "date": datetime(2024, 2, 10),
        "tags": ["节日", "联欢"],
        "participant_count": 20
    },
    {
        "title": "AI技术研讨会",
        "description": "探讨人工智能的最新发展，分享前沿技术和应用案例。",
        "date": datetime(2024, 5, 18),
        "tags": ["AI", "技术", "研讨"],
        "participant_count": 14
    },
    {
        "title": "夏季游戏竞赛",
        "description": "多样化游戏竞赛，展现团队协作精神，享受竞技的乐趣。",
        "date": datetime(2024, 8, 25),
        "tags": ["游戏", "竞赛"],
        "participant_count": 22
    }
]


async def create_sample_activities():
    """创建示例活动数据"""
    print("🚀 开始创建示例活动数据...")
    
    # 初始化数据库服务
    factory = DatabaseServiceFactory()
    db_service = factory.create(settings.database_url)
    set_database_service(db_service)

    try:
        # 创建数据库连接
        async with db_service.with_session() as session:
            # 获取所有成员ID
            all_members = await MemberCRUD.get_all(session)
            if not all_members:
                print("❌ 错误：数据库中没有成员数据，请先导入成员数据")
                return
            
            member_ids = [member.id for member in all_members]
            print(f"📊 找到 {len(member_ids)} 个成员")
            
            # 检查是否已有活动数据
            existing_activities = await ActivityCRUD.get_all(session)
            if existing_activities:
                print(f"⚠️  警告：数据库中已有 {len(existing_activities)} 个活动")
                response = input("是否要清除现有数据并重新创建？(y/N): ")
                if response.lower() == 'y':
                    for activity in existing_activities:
                        await ActivityCRUD.delete(session, activity.id)
                    print("🗑️  已清除现有活动数据")
                else:
                    print("❌ 操作已取消")
                    return
            
            # 创建示例活动
            created_count = 0
            for activity_data in SAMPLE_ACTIVITIES:
                # 随机选择参与成员
                participant_count = min(activity_data["participant_count"], len(member_ids))
                participant_ids = random.sample(member_ids, participant_count)
                
                # 创建活动
                activity_create = ActivityCreate(
                    title=activity_data["title"],
                    description=activity_data["description"],
                    date=activity_data["date"],
                    tags=activity_data["tags"],
                    participant_ids=participant_ids
                )
                
                try:
                    activity = await ActivityCRUD.create(session, activity_create)
                    created_count += 1
                    print(f"✅ 创建活动: {activity.title} (参与者: {len(participant_ids)}人)")
                except Exception as e:
                    print(f"❌ 创建活动失败: {activity_data['title']} - {str(e)}")
            
            print(f"\n🎉 成功创建 {created_count} 个示例活动！")
            
            # 显示统计信息
            total_activities = await ActivityCRUD.count_total(session)
            print(f"📈 数据库中共有 {total_activities} 个活动")
            
    except Exception as e:
        print(f"❌ 创建示例数据失败: {str(e)}")
        raise
    finally:
        await db_service.teardown()


async def main():
    """主函数"""
    try:
        await create_sample_activities()
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # 设置环境变量（如果未设置）
    if not os.getenv("DATABASE_URL"):
        print("⚠️  未找到DATABASE_URL环境变量，使用默认配置")
    
    asyncio.run(main())
