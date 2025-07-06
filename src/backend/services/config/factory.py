"""
配置服务工厂
"""
from __future__ import annotations

from .service import ConfigService


class ConfigServiceFactory:
    """配置服务工厂类"""

    def __init__(self) -> None:
        self.service_class = ConfigService

    def create(self) -> ConfigService:
        """创建配置服务实例

        Returns:
            ConfigService: 配置服务实例
        """
        return ConfigService()
