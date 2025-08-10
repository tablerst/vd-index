"""
Activity表的CRUD操作
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy import cast, literal
from sqlalchemy.dialects.postgresql import JSONB

from .base import Activity, ActivityCreate, ActivityRead, ActivityUpdate


class ActivityCRUD:
    """Activity表的CRUD操作类"""

    @staticmethod
    async def create(session: AsyncSession, activity_data: ActivityCreate) -> Activity:
        """创建新活动"""
        # 计算参与成员总数
        participants_total = len(activity_data.participant_ids)

        activity = Activity(
            **activity_data.model_dump(),
            participants_total=participants_total
        )
        session.add(activity)
        await session.commit()
        await session.refresh(activity)
        return activity

    @staticmethod
    async def get_by_id(session: AsyncSession, activity_id: int) -> Optional[Activity]:
        """根据ID获取活动"""
        return await session.get(Activity, activity_id)

    @staticmethod
    async def get_all(session: AsyncSession) -> List[Activity]:
        """获取所有活动"""
        statement = select(Activity).order_by(Activity.date.desc())
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_paginated(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "date"
    ) -> Tuple[List[Activity], int]:
        """分页获取活动列表"""
        # 计算偏移量
        offset = (page - 1) * page_size

        # 构建排序字段，默认按日期倒序
        if order_by == "date":
            order_field = Activity.date.desc()
        elif order_by == "title":
            order_field = Activity.title
        elif order_by == "created_at":
            order_field = Activity.created_at.desc()
        else:
            order_field = Activity.date.desc()

        # 查询活动
        statement = select(Activity).offset(offset).limit(page_size).order_by(order_field)
        result = await session.exec(statement)
        activities = result.all()

        # 查询总数
        count_statement = select(func.count(Activity.id))
        count_result = await session.exec(count_statement)
        total = count_result.one()

        return activities, total

    @staticmethod
    async def get_by_date_range(
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> List[Activity]:
        """根据日期范围获取活动"""
        statement = select(Activity).where(
            Activity.date >= start_date,
            Activity.date <= end_date
        ).order_by(Activity.date.desc())
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_by_tag(session: AsyncSession, tag: str) -> List[Activity]:
        """根据标签获取活动"""
        statement = select(Activity).where(
            Activity.tags.contains([tag])
        ).order_by(Activity.date.desc())
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_by_participant(session: AsyncSession, member_id: int) -> List[Activity]:
        """根据参与成员ID获取活动"""
        # Postgres JSONB contains 使用 @> 操作：column @> '[member_id]'
        # 但 SQLModel 的 contains 有时会退化为 LIKE。这里显式 cast 为 JSONB 并使用 @> 语义。
        arr_json = literal(f'[{member_id}]')
        statement = (
            select(Activity)
            .where(cast(Activity.participant_ids, JSONB).op("@>")(cast(arr_json, JSONB)))
            .order_by(Activity.date.desc())
        )
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def search_by_title(session: AsyncSession, keyword: str) -> List[Activity]:
        """根据标题关键词搜索活动"""
        statement = select(Activity).where(
            Activity.title.contains(keyword)
        ).order_by(Activity.date.desc())
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def search_by_description(session: AsyncSession, keyword: str) -> List[Activity]:
        """根据描述关键词搜索活动"""
        statement = select(Activity).where(
            Activity.description.contains(keyword)
        ).order_by(Activity.date.desc())
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def update(session: AsyncSession, activity_id: int, activity_data: ActivityUpdate) -> Optional[Activity]:
        """更新活动信息"""
        activity = await session.get(Activity, activity_id)
        if not activity:
            return None

        # 更新字段
        update_data = activity_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(activity, field, value)

        # 如果更新了参与成员列表，重新计算总数
        if 'participant_ids' in update_data:
            activity.participants_total = len(activity.participant_ids)

        # 更新时间戳
        activity.updated_at = datetime.utcnow()

        session.add(activity)
        await session.commit()
        await session.refresh(activity)
        return activity

    @staticmethod
    async def add_participant(session: AsyncSession, activity_id: int, member_id: int) -> Optional[Activity]:
        """为活动添加参与成员"""
        activity = await session.get(Activity, activity_id)
        if not activity:
            return None

        if member_id not in activity.participant_ids:
            activity.participant_ids.append(member_id)
            activity.participants_total = len(activity.participant_ids)
            activity.updated_at = datetime.utcnow()

            session.add(activity)
            await session.commit()
            await session.refresh(activity)

        return activity

    @staticmethod
    async def remove_participant(session: AsyncSession, activity_id: int, member_id: int) -> Optional[Activity]:
        """从活动中移除参与成员"""
        activity = await session.get(Activity, activity_id)
        if not activity:
            return None

        if member_id in activity.participant_ids:
            activity.participant_ids.remove(member_id)
            activity.participants_total = len(activity.participant_ids)
            activity.updated_at = datetime.utcnow()

            session.add(activity)
            await session.commit()
            await session.refresh(activity)

        return activity

    @staticmethod
    async def add_tag(session: AsyncSession, activity_id: int, tag: str) -> Optional[Activity]:
        """为活动添加标签"""
        activity = await session.get(Activity, activity_id)
        if not activity:
            return None

        if tag not in activity.tags:
            activity.tags.append(tag)
            activity.updated_at = datetime.utcnow()

            session.add(activity)
            await session.commit()
            await session.refresh(activity)

        return activity

    @staticmethod
    async def remove_tag(session: AsyncSession, activity_id: int, tag: str) -> Optional[Activity]:
        """从活动中移除标签"""
        activity = await session.get(Activity, activity_id)
        if not activity:
            return None
        if tag in activity.tags:
            activity.tags.remove(tag)
            activity.updated_at = datetime.utcnow()
            session.add(activity)
            await session.commit()
            await session.refresh(activity)
        return activity


    @staticmethod
    async def delete(session: AsyncSession, activity_id: int) -> bool:
        """删除活动"""
        activity = await session.get(Activity, activity_id)
        if not activity:
            return False

        await session.delete(activity)
        await session.commit()
        return True

    @staticmethod
    async def count_total(session: AsyncSession) -> int:
        """获取活动总数"""
        statement = select(func.count(Activity.id))
        result = await session.exec(statement)
        return result.one()

    @staticmethod
    async def count_by_tag(session: AsyncSession, tag: str) -> int:
        """根据标签统计活动数量"""
        statement = select(func.count(Activity.id)).where(
            Activity.tags.contains([tag])
        )
        result = await session.exec(statement)
        return result.one()

    @staticmethod
    async def get_latest_activities(session: AsyncSession, limit: int = 10) -> List[Activity]:
        """获取最新的活动"""
        statement = select(Activity).order_by(Activity.created_at.desc()).limit(limit)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_upcoming_activities(session: AsyncSession, limit: int = 10) -> List[Activity]:
        """获取即将到来的活动"""
        now = datetime.utcnow()
        statement = select(Activity).where(
            Activity.date > now
        ).order_by(Activity.date.asc()).limit(limit)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def bulk_create(session: AsyncSession, activities_data: List[ActivityCreate]) -> List[Activity]:
        """批量创建活动"""
        activities = []
        for activity_data in activities_data:
            participants_total = len(activity_data.participant_ids)
            activity = Activity(
                **activity_data.model_dump(),
                participants_total=participants_total
            )
            activities.append(activity)

        session.add_all(activities)
        await session.commit()

        # 刷新所有活动以获取ID
        for activity in activities:
            await session.refresh(activity)

        return activities

    @staticmethod
    async def get_all_tags(session: AsyncSession) -> List[str]:
        """获取所有使用过的标签"""
        statement = select(Activity.tags)
        result = await session.exec(statement)
        all_tags = result.all()

        # 展平标签列表并去重
        unique_tags = set()
        for tags in all_tags:
            unique_tags.update(tags)

        return sorted(list(unique_tags))
