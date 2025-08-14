"""
Config表的CRUD操作
"""
from datetime import datetime
from backend.services.database.models.base import now_naive
from typing import List, Optional, Dict, Any
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .base import Config, ConfigCreate, ConfigRead, ConfigUpdate


class ConfigCRUD:
    """Config表的CRUD操作类"""
    
    @staticmethod
    async def create(session: AsyncSession, config_data: ConfigCreate) -> Config:
        """创建新配置"""
        config = Config(**config_data.model_dump())
        session.add(config)
        await session.commit()
        await session.refresh(config)
        return config
    
    @staticmethod
    async def get_by_id(session: AsyncSession, config_id: int) -> Optional[Config]:
        """根据ID获取配置"""
        return await session.get(Config, config_id)

    @staticmethod
    async def get_by_key(session: AsyncSession, key: str) -> Optional[Config]:
        """根据key获取配置"""
        statement = select(Config).where(Config.key == key)
        result = await session.exec(statement)
        return result.first()
    
    @staticmethod
    async def get_value_by_key(session: AsyncSession, key: str) -> Optional[str]:
        """根据key获取配置值"""
        config = await session.get(Config, key)
        return config.value if config else None
    
    @staticmethod
    async def get_all(session: AsyncSession, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Config]:
        """获取所有配置"""
        statement = select(Config).order_by(Config.key)
        if limit is not None:
            statement = statement.limit(limit)
        if offset is not None:
            statement = statement.offset(offset)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def count_all(session: AsyncSession) -> int:
        """获取配置总数"""
        statement = select(func.count(Config.id))
        result = await session.exec(statement)
        return result.one()
    
    @staticmethod
    async def get_all_as_dict(session: AsyncSession) -> Dict[str, str]:
        """获取所有配置并返回为字典格式"""
        configs = await ConfigCRUD.get_all(session)
        return {config.key: config.value for config in configs}
    
    @staticmethod
    async def get_by_key_prefix(session: AsyncSession, prefix: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Config]:
        """根据key前缀获取配置"""
        statement = select(Config).where(Config.key.startswith(prefix)).order_by(Config.key)
        if limit is not None:
            statement = statement.limit(limit)
        if offset is not None:
            statement = statement.offset(offset)
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def count_by_key_prefix(session: AsyncSession, prefix: str) -> int:
        """获取指定前缀的配置总数"""
        statement = select(func.count(Config.id)).where(Config.key.startswith(prefix))
        result = await session.exec(statement)
        return result.one()
    
    @staticmethod
    async def search_by_description(session: AsyncSession, keyword: str) -> List[Config]:
        """根据描述关键词搜索配置"""
        statement = select(Config).where(
            Config.description.contains(keyword)
        ).order_by(Config.key)
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def update(session: AsyncSession, config_id: int, config_data: ConfigUpdate) -> Optional[Config]:
        """根据ID更新配置"""
        config = await session.get(Config, config_id)
        if not config:
            return None

        # 更新字段
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)

        # 更新时间戳
        config.updated_at = now_naive()

        session.add(config)
        await session.commit()
        await session.refresh(config)
        return config

    @staticmethod
    async def update_by_key(session: AsyncSession, key: str, config_data: ConfigUpdate) -> Optional[Config]:
        """根据key更新配置"""
        statement = select(Config).where(Config.key == key)
        result = await session.exec(statement)
        config = result.first()
        if not config:
            return None

        # 更新字段
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)

        # 更新时间戳
        config.updated_at = now_naive()

        session.add(config)
        await session.commit()
        await session.refresh(config)
        return config
    
    @staticmethod
    async def update_value(session: AsyncSession, key: str, value: str) -> Optional[Config]:
        """更新配置值"""
        config = await session.get(Config, key)
        if not config:
            return None
        
        config.value = value
        config.updated_at = now_naive()
        
        session.add(config)
        await session.commit()
        await session.refresh(config)
        return config
    
    @staticmethod
    async def upsert(session: AsyncSession, key: str, value: str, description: Optional[str] = None) -> Config:
        """插入或更新配置（如果key存在则更新，否则创建）"""
        config = await session.get(Config, key)
        
        if config:
            # 更新现有配置
            config.value = value
            if description is not None:
                config.description = description
            config.updated_at = now_naive()
        else:
            # 创建新配置
            config = Config(
                key=key,
                value=value,
                description=description
            )
        
        session.add(config)
        await session.commit()
        await session.refresh(config)
        return config
    
    @staticmethod
    async def delete(session: AsyncSession, config_id: int) -> bool:
        """根据ID删除配置"""
        config = await session.get(Config, config_id)
        if not config:
            return False

        await session.delete(config)
        await session.commit()
        return True

    @staticmethod
    async def delete_by_key(session: AsyncSession, key: str) -> bool:
        """根据key删除配置"""
        statement = select(Config).where(Config.key == key)
        result = await session.exec(statement)
        config = result.first()
        if not config:
            return False

        await session.delete(config)
        await session.commit()
        return True
    
    @staticmethod
    async def delete_by_prefix(session: AsyncSession, prefix: str) -> int:
        """根据key前缀批量删除配置"""
        statement = select(Config).where(Config.key.startswith(prefix))
        result = await session.exec(statement)
        configs = result.all()
        
        count = len(configs)
        for config in configs:
            await session.delete(config)
        
        await session.commit()
        return count
    
    @staticmethod
    async def exists(session: AsyncSession, key: str) -> bool:
        """检查配置是否存在"""
        config = await session.get(Config, key)
        return config is not None
    
    @staticmethod
    async def count_total(session: AsyncSession) -> int:
        """获取配置总数"""
        statement = select(func.count(Config.key))
        result = await session.exec(statement)
        return result.one()
    
    @staticmethod
    async def bulk_create(session: AsyncSession, configs_data: List[ConfigCreate]) -> List[Config]:
        """批量创建配置"""
        configs = [Config(**config_data.model_dump()) for config_data in configs_data]
        session.add_all(configs)
        await session.commit()
        
        # 刷新所有配置
        for config in configs:
            await session.refresh(config)
        
        return configs
    
    @staticmethod
    async def bulk_upsert(session: AsyncSession, config_dict: Dict[str, str]) -> List[Config]:
        """批量插入或更新配置"""
        configs = []
        
        for key, value in config_dict.items():
            config = await ConfigCRUD.upsert(session, key, value)
            configs.append(config)
        
        return configs
    
    @staticmethod
    async def get_latest_configs(session: AsyncSession, limit: int = 10) -> List[Config]:
        """获取最新更新的配置"""
        statement = select(Config).order_by(Config.updated_at.desc()).limit(limit)
        result = await session.exec(statement)
        return result.all()
