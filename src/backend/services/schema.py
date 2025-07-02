from enum import Enum


class ServiceType(str, Enum):
    """Enum for the different types of services that can be registered with the service manager."""

    DATABASE_SERVICE = "database_service"
