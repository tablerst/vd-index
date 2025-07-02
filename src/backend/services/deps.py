"""
数据库依赖注入模块
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from loguru import logger

from .schema import ServiceType

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from sqlmodel.ext.asyncio.session import AsyncSession
    from .database.service import DatabaseService

# 全局数据库服务实例
_database_service: DatabaseService | None = None


def get_service(service_type: ServiceType, default=None):
    """获取服务实例

    Args:
        service_type: 服务类型
        default: 默认服务工厂

    Returns:
        服务实例
    """
    if service_type == ServiceType.DATABASE_SERVICE:
        return get_db_service()

    if default:
        return default.create()

    raise ValueError(f"Unsupported service type: {service_type}")


def set_database_service(database_service: DatabaseService) -> None:
    """设置全局数据库服务实例"""
    global _database_service
    _database_service = database_service


def clear_database_service() -> None:
    """清除全局数据库服务实例（主要用于测试）"""
    global _database_service
    _database_service = None


def get_db_service() -> DatabaseService:
    """获取数据库服务实例

    Returns:
        DatabaseService: 数据库服务实例
    """
    if _database_service is None:
        raise ValueError("Database service not initialized. Call set_database_service() first.")
    return _database_service


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Retrieves an async session from the database service.

    Yields:
        AsyncSession: An async session object.

    """
    async with get_db_service().with_session() as session:
        yield session


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for managing an async session scope.

    This context manager is used to manage an async session scope for database operations.
    It ensures that the session is properly committed if no exceptions occur,
    and rolled back if an exception is raised.

    Yields:
        AsyncSession: The async session object.

    Raises:
        Exception: If an error occurs during the session scope.

    """
    db_service = get_db_service()
    async with db_service.with_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            logger.exception("An error occurred during the session scope.")
            await session.rollback()
            raise
