"""
数据库服务模块
支持 PostgreSQL + asyncpg + alembic
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import orjson
from alembic import command
from alembic.config import Config
from loguru import logger
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import retry, stop_after_attempt, wait_fixed

from . import models
from .models.base import orjson_dumps, orjson_dumps_compact


class DatabaseService:
    """数据库服务类，支持 PostgreSQL + asyncpg + alembic"""

    name = "database_service"

    def __init__(self, database_url: str):
        """初始化数据库服务

        Args:
            database_url: 数据库连接URL，格式为 postgresql+asyncpg://user:pass@host:port/db
        """
        if not database_url:
            raise ValueError("Database URL is required")

        self.database_url = database_url
        self._sanitize_database_url()

        # 设置 alembic 配置路径
        backend_dir = Path(__file__).parent.parent.parent
        self.script_location = backend_dir / "alembic"
        self.alembic_cfg_path = backend_dir / "alembic.ini"

        # 创建数据库引擎
        self.engine = self._create_engine()

    def _sanitize_database_url(self):
        """清理数据库URL，确保使用正确的方言"""
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql+asyncpg://")
            logger.warning(
                "Fixed postgres dialect in database URL. Replacing postgres:// with postgresql+asyncpg://. "
                "To avoid this warning, update the database URL."
            )
        elif self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")

    def _create_engine(self) -> AsyncEngine:
        """创建数据库引擎"""
        return create_async_engine(
            self.database_url,
            echo=False,  # 可以根据需要设置为 True 来调试 SQL
            pool_size=10,
            max_overflow=20,
            json_serializer=orjson_dumps_compact,
            json_deserializer=orjson.loads,
        )

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(10))
    def _create_engine_with_retry(self) -> AsyncEngine:
        """带重试的创建数据库引擎"""
        return self._create_engine()

    @asynccontextmanager
    async def with_session(self):
        """数据库会话上下文管理器"""
        async with AsyncSession(self.engine, expire_on_commit=False) as session:
            try:
                yield session
            except exc.SQLAlchemyError as db_exc:
                logger.error(f"Database error during session scope: {db_exc}")
                await session.rollback()
                raise

    async def create_db_and_tables(self) -> None:
        """创建数据库表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def run_migrations(self) -> None:
        """运行数据库迁移"""
        if not self.script_location.exists():
            logger.warning(f"Alembic script location not found: {self.script_location}")
            return

        alembic_cfg = Config(str(self.alembic_cfg_path))
        alembic_cfg.set_main_option("script_location", str(self.script_location))
        alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)

        try:
            await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
            logger.info("Database migrations completed successfully")
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            raise

    async def teardown(self) -> None:
        """清理数据库连接"""
        logger.debug("Tearing down database")
        await self.engine.dispose()
