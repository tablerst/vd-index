import pytest
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings
import logging

logger = logging.getLogger(__name__)


def _is_async_db(url: str) -> bool:
    """判断 URL 是否使用异步驱动"""
    return any(tok in url for tok in ("+asyncpg", "+aiomysql", "+asyncpyodbc"))


@pytest.mark.asyncio
async def test_database_connection():
    """简单执行 SELECT 1 判断数据库连接是否可用"""
    url = settings.database_url
    logger.debug(f"数据库连接URL: {url}")

    if _is_async_db(url):
        logger.info("使用异步数据库驱动")
        connect_args = {"server_settings": {"search_path": "public"}}
        engine = create_async_engine(url, echo=False, connect_args=connect_args)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        await engine.dispose()
    else:
        logger.info("使用同步数据库驱动")
        connect_args = {}
        engine = create_engine(url, echo=False, connect_args=connect_args)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        engine.dispose()
