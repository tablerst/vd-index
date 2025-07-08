"""
缓存监控API路由
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from services.deps import get_cache_service
from services.auth.utils import require_admin
from services.cache.service import CacheStats

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cache"])


@router.get(
    "/cache/stats",
    response_model=CacheStats,
    summary="获取缓存统计信息",
    description="获取缓存的命中率、大小等统计信息（需要管理员权限）"
)
async def get_cache_stats(_: dict = Depends(require_admin)):
    """获取缓存统计信息"""
    try:
        cache_service = get_cache_service()
        stats = await cache_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"获取缓存统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计信息失败: {str(e)}")


@router.post(
    "/cache/clear",
    summary="清空缓存",
    description="清空所有缓存数据（需要管理员权限）"
)
async def clear_cache(_: dict = Depends(require_admin)):
    """清空缓存"""
    try:
        cache_service = get_cache_service()
        await cache_service.clear()
        logger.info("缓存已清空")
        return {"message": "缓存已清空", "success": True}
    except Exception as e:
        logger.error(f"清空缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")


@router.delete(
    "/cache/key/{cache_key}",
    summary="删除指定缓存键",
    description="删除指定的缓存键（需要管理员权限）"
)
async def delete_cache_key(cache_key: str, _: dict = Depends(require_admin)):
    """删除指定缓存键"""
    try:
        cache_service = get_cache_service()
        deleted = await cache_service.delete(cache_key)
        if deleted:
            logger.info(f"缓存键 {cache_key} 已删除")
            return {"message": f"缓存键 {cache_key} 已删除", "success": True}
        else:
            return {"message": f"缓存键 {cache_key} 不存在", "success": False}
    except Exception as e:
        logger.error(f"删除缓存键失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除缓存键失败: {str(e)}")
