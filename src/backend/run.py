#!/usr/bin/env python3
"""
后端服务启动脚本
"""
import uvicorn
from services.config.factory import ConfigServiceFactory

if __name__ == "__main__":
    # 初始化配置服务
    config_factory = ConfigServiceFactory()
    config_service = config_factory.create()
    settings = config_service.get_settings()

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=True
    )
