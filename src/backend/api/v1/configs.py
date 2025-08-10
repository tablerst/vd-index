"""
配置管理API路由
"""
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session
from services.auth.utils import require_admin
from services.database.models.config.base import Config, ConfigCreate, ConfigUpdate
from services.database.models.config.crud import ConfigCRUD
from schema.config import (
    ConfigResponse,
    ConfigListResponse,
    ConfigCreateRequest,
    ConfigUpdateRequest,
    ApiResponse
)

router = APIRouter(prefix="/configs", tags=["configs"])


@router.get(
    "",
    response_model=ConfigListResponse,
    summary="获取配置列表",
    description="分页获取系统配置列表"
)
async def get_configs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    key_prefix: Optional[str] = Query(None, description="配置键前缀过滤"),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """获取配置列表"""
    try:
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取配置列表和总数
        if key_prefix:
            configs = await ConfigCRUD.get_by_key_prefix(session, key_prefix, limit=page_size, offset=offset)
            total = await ConfigCRUD.count_by_key_prefix(session, key_prefix)
        else:
            configs = await ConfigCRUD.get_all(session, limit=page_size, offset=offset)
            total = await ConfigCRUD.count_all(session)
        
        # 计算总页数
        total_pages = math.ceil(total / page_size)
        
        return ConfigListResponse(
            configs=[ConfigResponse.model_validate(config) for config in configs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置列表失败: {str(e)}")


@router.get(
    "/{config_id}",
    response_model=ConfigResponse,
    summary="获取单个配置",
    description="根据ID获取配置详情"
)
async def get_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """获取单个配置"""
    config = await ConfigCRUD.get_by_id(session, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return ConfigResponse.model_validate(config)


@router.get(
    "/key/{key}",
    response_model=ConfigResponse,
    summary="根据键获取配置",
    description="根据配置键获取配置详情"
)
async def get_config_by_key(
    key: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """根据键获取配置"""
    config = await ConfigCRUD.get_by_key(session, key)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return ConfigResponse.model_validate(config)


@router.post(
    "",
    response_model=ConfigResponse,
    summary="创建配置",
    description="创建新的系统配置"
)
async def create_config(
    config_data: ConfigCreateRequest,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """创建配置"""
    try:
        # 检查配置键是否已存在
        existing_config = await ConfigCRUD.get_by_key(session, config_data.key)
        if existing_config:
            raise HTTPException(status_code=400, detail="配置键已存在")
        
        # 验证配置值格式
        _validate_config_value(config_data.type, config_data.value)
        
        # 创建配置
        config_create = ConfigCreate(
            key=config_data.key,
            value=config_data.value,
            description=config_data.description,
            type=config_data.type,
            is_active=config_data.is_active
        )
        
        config = await ConfigCRUD.create(session, config_create)
        return ConfigResponse.model_validate(config)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建配置失败: {str(e)}")


@router.put(
    "/{config_id}",
    response_model=ConfigResponse,
    summary="更新配置",
    description="更新现有配置"
)
async def update_config(
    config_id: int,
    config_data: ConfigUpdateRequest,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """更新配置"""
    try:
        # 检查配置是否存在
        config = await ConfigCRUD.get_by_id(session, config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 验证配置值格式（如果提供了新值）
        if config_data.value is not None:
            config_type = config_data.type if config_data.type is not None else config.type
            _validate_config_value(config_type, config_data.value)
        
        # 更新配置
        config_update = ConfigUpdate(**config_data.model_dump(exclude_unset=True))
        updated_config = await ConfigCRUD.update(session, config_id, config_update)
        
        return ConfigResponse.model_validate(updated_config)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.delete(
    "/{config_id}",
    response_model=ApiResponse,
    summary="删除配置",
    description="删除指定配置"
)
async def delete_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """删除配置"""
    try:
        # 检查配置是否存在
        config = await ConfigCRUD.get_by_id(session, config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 删除配置
        success = await ConfigCRUD.delete(session, config_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除配置失败")
        
        return ApiResponse(
            success=True,
            message="配置删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")


def _validate_config_value(config_type: str, value: str) -> None:
    """验证配置值格式"""
    if config_type == "number":
        try:
            float(value)
        except ValueError:
            raise HTTPException(status_code=400, detail="数字类型配置值格式不正确")
    
    elif config_type == "boolean":
        if value.lower() not in ["true", "false", "1", "0"]:
            raise HTTPException(status_code=400, detail="布尔类型配置值只能是 true/false 或 1/0")
    
    elif config_type == "json":
        try:
            import json
            json.loads(value)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="JSON类型配置值格式不正确")
