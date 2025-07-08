"""
API路由管理器
统一管理所有API版本的路由
"""
from fastapi import APIRouter

# 导入v1版本的路由
from api.v1 import members, avatars, admin, activities, auth, setup, configs, cache

# 创建v1路由器
v1_router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)

# 注册v1版本的路由
v1_router.include_router(auth.router)
v1_router.include_router(setup.router)
v1_router.include_router(members.router)
v1_router.include_router(avatars.router)
v1_router.include_router(admin.router)
v1_router.include_router(activities.router)
v1_router.include_router(configs.router)
v1_router.include_router(cache.router)

# 主路由器，包含所有版本
main_router = APIRouter()

# 注册v1路由
main_router.include_router(v1_router)

# 为了向后兼容，也可以添加其他版本的路由
# 例如：
# v2_router = APIRouter(prefix="/api/v2")
# main_router.include_router(v2_router)
