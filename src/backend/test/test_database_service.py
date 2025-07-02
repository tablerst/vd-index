"""
数据库服务适配测试
测试新的简化数据库服务架构
"""
import os
import pytest
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.database.service import DatabaseService
from services.database.factory import DatabaseServiceFactory
from services.deps import set_database_service, get_db_service, clear_database_service


@pytest.fixture
def database_url():
    """获取数据库URL"""
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL environment variable not set")
    return url


@pytest.fixture
async def db_service(database_url):
    """创建数据库服务实例"""
    factory = DatabaseServiceFactory()
    service = factory.create(database_url)
    
    # 设置全局服务
    set_database_service(service)
    
    yield service
    
    # 清理
    await service.teardown()
    clear_database_service()


class TestDatabaseService:
    """数据库服务测试类"""
    
    @pytest.mark.asyncio
    async def test_database_service_creation(self, database_url):
        """测试数据库服务创建"""
        factory = DatabaseServiceFactory()
        service = factory.create(database_url)
        
        assert service is not None
        assert isinstance(service, DatabaseService)
        assert service.database_url == database_url
        
        # 清理
        await service.teardown()
    
    @pytest.mark.asyncio
    async def test_database_connection(self, db_service):
        """测试数据库连接"""
        # 测试会话管理器
        async with db_service.with_session() as session:
            assert session is not None
            # 执行简单查询验证连接
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
    
    @pytest.mark.asyncio
    async def test_create_tables(self, db_service):
        """测试创建数据库表"""
        # 这个操作应该是幂等的
        await db_service.create_db_and_tables()
        
        # 再次调用应该不会出错
        await db_service.create_db_and_tables()
    
    @pytest.mark.asyncio
    async def test_run_migrations(self, db_service):
        """测试运行数据库迁移"""
        # 运行迁移
        await db_service.run_migrations()
        
        # 再次运行应该不会出错（幂等性）
        await db_service.run_migrations()
    
    @pytest.mark.asyncio
    async def test_dependency_injection(self, db_service):
        """测试依赖注入系统"""
        # 测试获取全局数据库服务
        retrieved_service = get_db_service()
        assert retrieved_service is db_service
        
        # 测试会话依赖
        from services.deps import get_session
        async for session in get_session():
            assert session is not None
            break  # 只测试第一个会话
    
    @pytest.mark.asyncio
    async def test_session_scope(self, db_service):
        """测试会话作用域管理"""
        from services.deps import session_scope
        
        async with session_scope() as session:
            assert session is not None
            # 在会话中执行操作
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1


class TestDatabaseModels:
    """数据库模型测试类"""
    
    def test_member_model_import(self):
        """测试 Member 模型导入"""
        from services.database.models.member import Member
        assert Member is not None
        
        # 检查模型字段
        assert hasattr(Member, 'id')
        assert hasattr(Member, 'display_name')
        assert hasattr(Member, 'uin_encrypted')
        assert hasattr(Member, 'role')
        assert hasattr(Member, 'join_time')
    
    def test_config_model_import(self):
        """测试 Config 模型导入"""
        from services.database.models.config import Config
        assert Config is not None
        
        # 检查模型字段
        assert hasattr(Config, 'key')
        assert hasattr(Config, 'value')
    
    def test_models_metadata(self):
        """测试模型元数据"""
        from sqlmodel import SQLModel
        # 导入所有模型以确保它们被注册到元数据中
        from services.database.models.member import Member  # noqa: F401
        from services.database.models.config import Config  # noqa: F401

        # 检查元数据中是否包含我们的表
        table_names = [table.name for table in SQLModel.metadata.tables.values()]
        assert 'members' in table_names
        assert 'config' in table_names


@pytest.mark.asyncio
async def test_full_database_workflow(database_url):
    """完整的数据库工作流测试"""
    # 创建服务
    factory = DatabaseServiceFactory()
    service = factory.create(database_url)
    set_database_service(service)
    
    try:
        # 1. 测试连接
        async with service.with_session() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        # 2. 创建表
        await service.create_db_and_tables()
        
        # 3. 运行迁移
        await service.run_migrations()
        
        # 4. 测试依赖注入
        retrieved_service = get_db_service()
        assert retrieved_service is service
        
    finally:
        # 清理
        await service.teardown()
        clear_database_service()


if __name__ == "__main__":
    # 如果直接运行此文件，执行 pytest
    import subprocess
    import sys
    
    print("运行数据库服务测试...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        __file__, "-v", "--tb=short"
    ], cwd=backend_dir)
    
    sys.exit(result.returncode)
