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
    from .auth.service import AuthService
    from .config.service import ConfigService
    from .crypto.service import CryptoService

# 全局服务实例
_database_service: DatabaseService | None = None
_auth_service: AuthService | None = None
_config_service: ConfigService | None = None
_crypto_service: CryptoService | None = None


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
    elif service_type == ServiceType.AUTH_SERVICE:
        return get_auth_service()
    elif service_type == ServiceType.CONFIG_SERVICE:
        return get_config_service()
    elif service_type == ServiceType.CRYPTO_SERVICE:
        return get_crypto_service()

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


def set_auth_service(auth_service: AuthService) -> None:
    """设置全局认证服务实例"""
    global _auth_service
    _auth_service = auth_service


def clear_auth_service() -> None:
    """清除全局认证服务实例（主要用于测试）"""
    global _auth_service
    _auth_service = None


def set_config_service(config_service: ConfigService) -> None:
    """设置全局配置服务实例"""
    global _config_service
    _config_service = config_service


def clear_config_service() -> None:
    """清除全局配置服务实例（主要用于测试）"""
    global _config_service
    _config_service = None


def set_crypto_service(crypto_service: CryptoService) -> None:
    """设置全局加密服务实例"""
    global _crypto_service
    _crypto_service = crypto_service


def clear_crypto_service() -> None:
    """清除全局加密服务实例（主要用于测试）"""
    global _crypto_service
    _crypto_service = None


def get_db_service() -> DatabaseService:
    """获取数据库服务实例

    Returns:
        DatabaseService: 数据库服务实例
    """
    if _database_service is None:
        raise ValueError("Database service not initialized. Call set_database_service() first.")
    return _database_service


def get_auth_service() -> AuthService:
    """获取认证服务实例

    Returns:
        AuthService: 认证服务实例
    """
    if _auth_service is None:
        raise ValueError("Auth service not initialized. Call set_auth_service() first.")
    return _auth_service


def get_config_service() -> ConfigService:
    """获取配置服务实例

    Returns:
        ConfigService: 配置服务实例
    """
    if _config_service is None:
        raise ValueError("Config service not initialized. Call set_config_service() first.")
    return _config_service


def get_crypto_service() -> CryptoService:
    """获取加密服务实例

    Returns:
        CryptoService: 加密服务实例
    """
    if _crypto_service is None:
        raise ValueError("Crypto service not initialized. Call set_crypto_service() first.")
    return _crypto_service


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
