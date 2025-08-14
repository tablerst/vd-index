"""
用户CRUD操作
"""
from datetime import datetime
from backend.services.database.models.base import now_naive
from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import User, UserCreate, UserUpdate


class UserCRUD:
    """用户CRUD操作类"""

    @staticmethod
    async def create(session: AsyncSession, user_create: UserCreate, password_hash: str) -> User:
        """创建用户"""
        user = User(
            username=user_create.username,
            password_hash=password_hash,
            role=user_create.role,
            is_active=user_create.is_active
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return await session.get(User, user_id)

    @staticmethod
    async def get_by_username(session: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_by_member_id(session: AsyncSession, member_id: int) -> Optional[User]:
        """根据成员ID获取用户（绑定校验用）"""
        statement = select(User).where(User.member_id == member_id)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        statement = select(User).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def update(session: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户"""
        user = await session.get(User, user_id)
        if not user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = now_naive()
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update_last_login(session: AsyncSession, user_id: int) -> Optional[User]:
        """更新最后登录时间"""
        user = await session.get(User, user_id)
        if not user:
            return None

        user.last_login = now_naive()
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete(session: AsyncSession, user_id: int) -> bool:
        """删除用户"""
        user = await session.get(User, user_id)
        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True

    @staticmethod
    async def count(session: AsyncSession) -> int:
        """获取用户总数"""
        statement = select(User)
        result = await session.exec(statement)
        return len(result.all())
