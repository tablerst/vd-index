"""
测试配置文件
提供测试所需的fixtures
"""
import os
import pytest
import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from services.database.factory import DatabaseServiceFactory
from services.deps import set_database_service, clear_database_service, session_scope


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def database_url():
    """获取测试数据库URL"""
    url = os.getenv("DATABASE_URL")
    if not url:
        # 使用内存SQLite数据库进行测试
        url = "sqlite+aiosqlite:///:memory:"
    return url


@pytest.fixture
async def db_service(database_url):
    """创建数据库服务实例"""
    # 使用内存SQLite数据库进行测试
    test_url = "sqlite+aiosqlite:///:memory:"
    factory = DatabaseServiceFactory()
    service = factory.create(test_url)

    # 设置全局数据库服务
    set_database_service(service)

    # 初始化数据库
    await service.initialize()

    yield service

    # 清理
    await service.close()
    clear_database_service()


@pytest.fixture
async def async_session(db_service):
    """创建异步数据库会话"""
    async with session_scope() as session:
        yield session
