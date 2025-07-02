"""
数据库服务工厂
"""
from __future__ import annotations

from .service import DatabaseService


class DatabaseServiceFactory:
    """数据库服务工厂类"""

    def __init__(self) -> None:
        self.service_class = DatabaseService

    def create(self, database_url: str) -> DatabaseService:
        """创建数据库服务实例

        Args:
            database_url: 数据库连接URL

        Returns:
            DatabaseService: 数据库服务实例
        """
        if not database_url:
            raise ValueError("Database URL is required")
        return DatabaseService(database_url)
