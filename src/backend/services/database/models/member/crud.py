"""
Member表的CRUD操作
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .base import Member, MemberCreate, MemberRead, MemberUpdate
from services.deps import get_cache_service, get_config_service


def _get_member_cache_ttl() -> int:
    """获取成员缓存TTL配置"""
    try:
        config_service = get_config_service()
        settings = config_service.get_settings()
        return settings.cache_member_ttl
    except Exception:
        return 300  # 默认5分钟


class MemberCRUD:
    """Member表的CRUD操作类"""

    @staticmethod
    async def create(session: AsyncSession, member_data: MemberCreate) -> Member:
        """创建新成员"""
        member = Member(**member_data.model_dump())
        session.add(member)
        await session.commit()
        await session.refresh(member)

        # 更新缓存
        try:
            cache_service = get_cache_service()
            cache_key = f"member:id:{member.id}"
            ttl = _get_member_cache_ttl()
            await cache_service.set(cache_key, member, ttl=ttl)
        except Exception as e:
            # 缓存失败不影响主要功能
            import logging
            logging.getLogger(__name__).warning(f"Failed to cache member {member.id}: {e}")

        return member

    @staticmethod
    async def get_by_id(session: AsyncSession, member_id: int) -> Optional[Member]:
        """根据ID获取成员（带缓存）"""
        # 先尝试从缓存获取
        try:
            cache_service = get_cache_service()
            cache_key = f"member:id:{member_id}"
            cached_member = await cache_service.get(cache_key)
            if cached_member is not None:
                return cached_member
        except Exception as e:
            # 缓存失败不影响主要功能
            import logging
            logging.getLogger(__name__).warning(f"Failed to get member {member_id} from cache: {e}")

        # 缓存未命中，从数据库获取
        member = await session.get(Member, member_id)

        # 如果找到成员，存入缓存
        if member is not None:
            try:
                cache_service = get_cache_service()
                cache_key = f"member:id:{member_id}"
                ttl = _get_member_cache_ttl()
                await cache_service.set(cache_key, member, ttl=ttl)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to cache member {member_id}: {e}")

        return member
    
    @staticmethod
    async def get_by_uin_encrypted(session: AsyncSession, uin_encrypted: str) -> Optional[Member]:
        """根据加密UIN获取成员"""
        statement = select(Member).where(Member.uin_encrypted == uin_encrypted)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_many_by_ids(session: AsyncSession, member_ids: List[int]) -> Dict[int, Optional[Member]]:
        """批量获取成员（带缓存优化）"""
        result = {}
        uncached_ids = []

        # 先尝试从缓存获取
        try:
            cache_service = get_cache_service()
            cache_keys = [f"member:id:{member_id}" for member_id in member_ids]
            cached_members = await cache_service.get_many(cache_keys)

            for i, member_id in enumerate(member_ids):
                cache_key = cache_keys[i]
                cached_member = cached_members.get(cache_key)
                if cached_member is not None:
                    result[member_id] = cached_member
                else:
                    uncached_ids.append(member_id)
        except Exception as e:
            # 缓存失败，全部从数据库获取
            import logging
            logging.getLogger(__name__).warning(f"Failed to get members from cache: {e}")
            uncached_ids = member_ids

        # 从数据库批量获取未缓存的成员
        if uncached_ids:
            statement = select(Member).where(Member.id.in_(uncached_ids))
            db_result = await session.exec(statement)
            db_members = db_result.all()

            # 更新结果和缓存
            cache_items = {}
            for member in db_members:
                result[member.id] = member
                cache_items[f"member:id:{member.id}"] = member

            # 为未找到的ID设置None
            for member_id in uncached_ids:
                if member_id not in result:
                    result[member_id] = None

            # 批量更新缓存
            if cache_items:
                try:
                    cache_service = get_cache_service()
                    ttl = _get_member_cache_ttl()
                    await cache_service.set_many(cache_items, ttl=ttl)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Failed to cache members: {e}")

        return result

    @staticmethod
    async def get_all(session: AsyncSession) -> List[Member]:
        """获取所有成员"""
        statement = select(Member).order_by(Member.id)
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def get_paginated(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        order_by: str = "id"
    ) -> Tuple[List[Member], int]:
        """分页获取成员列表"""
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 构建排序字段
        order_field = getattr(Member, order_by, Member.id)
        
        # 查询成员
        statement = select(Member).offset(offset).limit(page_size).order_by(order_field)
        result = await session.exec(statement)
        members = result.all()
        
        # 查询总数
        count_statement = select(func.count(Member.id))
        count_result = await session.exec(count_statement)
        total = count_result.one()
        
        return members, total
    
    @staticmethod
    async def get_by_role(session: AsyncSession, role: int) -> List[Member]:
        """根据角色获取成员"""
        statement = select(Member).where(Member.role == role).order_by(Member.id)
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def get_by_display_name(session: AsyncSession, display_name: str) -> List[Member]:
        """根据显示名称搜索成员（模糊匹配）"""
        statement = select(Member).where(Member.display_name.contains(display_name)).order_by(Member.id)
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def update(session: AsyncSession, member_id: int, member_data: MemberUpdate) -> Optional[Member]:
        """更新成员信息"""
        member = await session.get(Member, member_id)
        if not member:
            return None

        # 更新字段
        update_data = member_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)

        # 更新时间戳
        member.updated_at = datetime.utcnow()

        session.add(member)
        await session.commit()
        await session.refresh(member)

        # 更新缓存
        try:
            cache_service = get_cache_service()
            cache_key = f"member:id:{member_id}"
            ttl = _get_member_cache_ttl()
            await cache_service.set(cache_key, member, ttl=ttl)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to update cache for member {member_id}: {e}")

        return member
    
    @staticmethod
    async def delete(session: AsyncSession, member_id: int) -> bool:
        """删除成员"""
        member = await session.get(Member, member_id)
        if not member:
            return False

        await session.delete(member)
        await session.commit()

        # 删除缓存
        try:
            cache_service = get_cache_service()
            cache_key = f"member:id:{member_id}"
            await cache_service.delete(cache_key)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to delete cache for member {member_id}: {e}")

        return True
    
    @staticmethod
    async def count_total(session: AsyncSession) -> int:
        """获取成员总数"""
        statement = select(func.count(Member.id))
        result = await session.exec(statement)
        return result.one()
    
    @staticmethod
    async def count_by_role(session: AsyncSession, role: int) -> int:
        """根据角色统计成员数量"""
        statement = select(func.count(Member.id)).where(Member.role == role)
        result = await session.exec(statement)
        return result.one()
    
    @staticmethod
    async def get_latest_members(session: AsyncSession, limit: int = 10) -> List[Member]:
        """获取最新加入的成员"""
        statement = select(Member).order_by(Member.created_at.desc()).limit(limit)
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def get_active_members(session: AsyncSession, days: int = 30) -> List[Member]:
        """获取最近活跃的成员（根据最后发言时间）"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        statement = select(Member).where(
            Member.last_speak_time >= cutoff_date
        ).order_by(Member.last_speak_time.desc())
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def bulk_create(session: AsyncSession, members_data: List[MemberCreate]) -> List[Member]:
        """批量创建成员"""
        members = [Member(**member_data.model_dump()) for member_data in members_data]
        session.add_all(members)
        await session.commit()

        # 刷新所有成员以获取ID
        for member in members:
            await session.refresh(member)

        # 批量更新缓存
        try:
            cache_service = get_cache_service()
            cache_items = {}
            for member in members:
                cache_key = f"member:id:{member.id}"
                cache_items[cache_key] = member

            if cache_items:
                ttl = _get_member_cache_ttl()
                await cache_service.set_many(cache_items, ttl=ttl)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to cache bulk created members: {e}")

        return members
    
    @staticmethod
    async def exists_by_uin_encrypted(session: AsyncSession, uin_encrypted: str) -> bool:
        """检查加密UIN是否已存在"""
        statement = select(func.count(Member.id)).where(Member.uin_encrypted == uin_encrypted)
        result = await session.exec(statement)
        return result.one() > 0
