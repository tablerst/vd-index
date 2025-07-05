
from sqlmodel import create_engine, Session
from core.config import settings

# 数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug
)

def create_db_and_tables():
    """创建数据库和表"""
    from sqlmodel import SQLModel  # Import here to avoid circular dependency
    # 导入所有模型以确保它们被注册到元数据中
    from backend.services.database.models import Member, Config, Activity  # noqa: F401
    SQLModel.metadata.create_all(engine)

def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
