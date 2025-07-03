
from sqlmodel import create_engine, Session
from core.config import settings

# 数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

def create_db_and_tables():
    """创建数据库和表"""
    from services.database.models.member import SQLModel  # Import here to avoid circular dependency
    SQLModel.metadata.create_all(engine)

def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
