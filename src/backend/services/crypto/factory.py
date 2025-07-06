"""
加密服务工厂
"""
from __future__ import annotations

from .service import CryptoService


class CryptoServiceFactory:
    """加密服务工厂类"""

    def __init__(self) -> None:
        self.service_class = CryptoService

    def create(self, config_service) -> CryptoService:
        """创建加密服务实例

        Args:
            config_service: 配置服务实例

        Returns:
            CryptoService: 加密服务实例
        """
        if not config_service:
            raise ValueError("Config service is required")
        return CryptoService(config_service)
