"""
Member表的CRUD操作
"""
from datetime import datetime
from typing import List, Optional, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .base import Member, MemberCreate, MemberRead, MemberUpdate


class MemberCRUD:
    """Member表的CRUD操作类"""
    
    @staticmethod
    async def create(session: AsyncSession, member_data: MemberCreate) -> Member:
        """创建新成员"""
        member = Member(**member_data.model_dump())
        session.add(member)
        await session.commit()
        await session.refresh(member)
        return member
    
    @staticmethod
    async def get_by_id(session: AsyncSession, member_id: int) -> Optional[Member]:
        """根据ID获取成员"""
        return await session.get(Member, member_id)
    
    @staticmethod
    async def get_by_uin_encrypted(session: AsyncSession, uin_encrypted: str) -> Optional[Member]:
        """根据加密UIN获取成员"""
        statement = select(Member).where(Member.uin_encrypted == uin_encrypted)
        result = await session.exec(statement)
        return result.first()
    
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
        return member
    
    @staticmethod
    async def delete(session: AsyncSession, member_id: int) -> bool:
        """删除成员"""
        member = await session.get(Member, member_id)
        if not member:
            return False
        
        await session.delete(member)
        await session.commit()
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
        
        return members
    
    @staticmethod
    async def exists_by_uin_encrypted(session: AsyncSession, uin_encrypted: str) -> bool:
        """检查加密UIN是否已存在"""
        statement = select(func.count(Member.id)).where(Member.uin_encrypted == uin_encrypted)
        result = await session.exec(statement)
        return result.one() > 0
