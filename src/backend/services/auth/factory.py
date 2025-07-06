"""
认证服务工厂
"""
from services.deps import get_config_service
from .service import AuthService


class AuthServiceFactory:
    """认证服务工厂"""

    def create(self) -> AuthService:
        """创建认证服务实例"""
        config_service = get_config_service()
        settings = config_service.get_settings()
        return AuthService(settings)
