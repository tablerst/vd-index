"""
FastAPI主应用
"""
import time
import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services.database.service import DatabaseService
from services.database.factory import DatabaseServiceFactory
from services.auth.factory import AuthServiceFactory
from services.config.factory import ConfigServiceFactory
from services.crypto.factory import CryptoServiceFactory
from services.deps import set_database_service, set_auth_service, set_config_service, set_crypto_service
from services.auth.utils import create_super_user
from services.database.models.user import User
from sqlmodel import select
from api.router import main_router

# 初始化全局配置服务
config_factory = ConfigServiceFactory()
config_service = config_factory.create()
settings = config_service.get_settings()


def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)

    # 设置日志级别
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 设置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器
    file_handler = logging.FileHandler(log_dir / "app.log", encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 错误日志文件处理器
    error_handler = logging.FileHandler(log_dir / "error.log", encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # 设置特定模块的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    print(f"✅ 日志配置完成 - 级别: {log_level}, 目录: {log_dir}")


# 初始化日志
setup_logging()
logger = logging.getLogger(__name__)


# 速率限制器
limiter = Limiter(key_func=get_remote_address)


async def ensure_admin_user_exists(db_service, auth_service, config_service, logger):
    """
    确保系统中存在管理员用户
    如果不存在，则从环境变量中读取配置创建管理员用户
    """
    try:
        # 获取数据库会话
        async with db_service.with_session() as session:
            # 检查是否已存在管理员用户
            admin_statement = select(User).where(User.role == "admin")
            result = await session.exec(admin_statement)
            existing_admins = result.all()

            if existing_admins:
                logger.info(f"✅ 管理员用户已存在: {[admin.username for admin in existing_admins]}")
                return

            # 没有管理员用户，从配置创建
            settings = config_service.get_settings()

            if not settings.super_user_username or not settings.super_user_password:
                logger.warning("⚠️  未配置超级用户信息，跳过管理员用户创建")
                logger.warning("   请在.env文件中设置 SUPER_USER_USERNAME 和 SUPER_USER_PASSWORD")
                return

            logger.info(f"🔧 创建管理员用户: {settings.super_user_username}")

            # 创建管理员用户
            admin_user = await create_super_user(
                session=session,
                auth_service=auth_service,
                username=settings.super_user_username,
                password=settings.super_user_password,
                email=settings.super_user_email or f"{settings.super_user_username}@example.com"
            )

            logger.info(f"✅ 管理员用户创建成功: {admin_user.username}")

    except Exception as e:
        logger.error(f"❌ 创建管理员用户失败: {str(e)}")
        # 不抛出异常，避免影响应用启动
        import traceback
        logger.error(traceback.format_exc())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 启动后端服务...")

    # 初始化配置服务
    config_factory = ConfigServiceFactory()
    config_service = config_factory.create()
    set_config_service(config_service)
    settings = config_service.get_settings()

    logger.info(f"调试模式: {settings.debug}")
    logger.info(f"数据库URL: {settings.database_url}")
    logger.info(f"头像根目录: {settings.avatar_root}")

    # 初始化加密服务
    crypto_factory = CryptoServiceFactory()
    crypto_service = crypto_factory.create(config_service)
    set_crypto_service(crypto_service)

    # 初始化数据库服务
    db_factory = DatabaseServiceFactory()
    db_service = db_factory.create(settings.database_url)
    set_database_service(db_service)

    # 初始化认证服务
    auth_factory = AuthServiceFactory()
    auth_service = auth_factory.create()
    set_auth_service(auth_service)

    # 创建数据库和表
    await db_service.create_db_and_tables()
    logger.info("✅ 数据库初始化完成")
    logger.info("✅ 认证服务初始化完成")

    # 确保必要的目录存在
    from pathlib import Path
    Path(settings.avatar_root).mkdir(parents=True, exist_ok=True)
    Path("./data").mkdir(parents=True, exist_ok=True)
    logger.info("✅ 目录结构初始化完成")

    # 检查并创建管理员账户
    await ensure_admin_user_exists(db_service, auth_service, config_service, logger)

    yield

    # 关闭时执行
    logger.info("🛑 关闭后端服务...")
    await db_service.teardown()


# 创建FastAPI应用
app = FastAPI(
    title="VD群成员管理API",
    description="VRC Division群成员信息安全管理后端服务",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# 添加速率限制
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# 中间件配置
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加处理时间头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# 信任主机中间件（生产环境）
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )


# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    if settings.debug:
        import traceback
        detail = traceback.format_exc()
    else:
        detail = "内部服务器错误"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "detail": detail if settings.debug else None
        }
    )


# 注册路由
app.include_router(main_router)


# API根路径（仅开发环境）
if settings.debug:
    @app.get("/", summary="API根路径")
    @limiter.limit(f"{settings.rate_limit_requests}/minute")
    async def root(request: Request):
        """API根路径"""
        return {
            "message": "VD群成员管理API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs" if settings.debug else "disabled"
        }


# 静态文件服务配置
static_dir = Path(__file__).parent.parent / "static"

# 生产环境：挂载前端静态文件
if static_dir.exists():
    print(f"📁 静态文件目录: {static_dir}")
    if not settings.debug:
        # 生产模式：挂载到根路径
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
        print("✅ 生产模式：静态文件服务已启用")
    else:
        # 开发模式：挂载到 /static 路径（可选，用于测试）
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print("✅ 开发模式：静态文件服务已启用（/static 路径）")
else:
    if not settings.debug:
        print("⚠️  警告：生产模式下未找到静态文件目录，请先运行构建脚本")


# 健康检查
@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
