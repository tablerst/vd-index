from enum import Enum


class ServiceType(str, Enum):
    """Enum for the different types of services that can be registered with the service manager."""

    DATABASE_SERVICE = "database_service"
    AUTH_SERVICE = "auth_service"
    CONFIG_SERVICE = "config_service"
    CRYPTO_SERVICE = "crypto_service"
    CACHE_SERVICE = "cache_service"
