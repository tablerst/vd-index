"""
Config模块导出
"""
from .base import Config, ConfigCreate, ConfigRead, ConfigUpdate
from .crud import ConfigCRUD

__all__ = [
    "Config", "ConfigCreate", "ConfigRead", "ConfigUpdate",
    "ConfigCRUD"
]
