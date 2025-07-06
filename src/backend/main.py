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

from core.config import settings
from services.database.service import DatabaseService
from services.database.factory import DatabaseServiceFactory
from services.deps import set_database_service
from api.router import main_router


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 启动后端服务...")
    logger.info(f"调试模式: {settings.debug}")
    logger.info(f"数据库URL: {settings.database_url}")
    logger.info(f"头像根目录: {settings.avatar_root}")

    # 初始化数据库服务
    factory = DatabaseServiceFactory()
    db_service = factory.create(settings.database_url)
    set_database_service(db_service)

    # 创建数据库和表
    await db_service.create_db_and_tables()
    logger.info("✅ 数据库初始化完成")

    # 确保必要的目录存在
    from pathlib import Path
    Path(settings.avatar_root).mkdir(parents=True, exist_ok=True)
    Path("./data").mkdir(parents=True, exist_ok=True)
    logger.info("✅ 目录结构初始化完成")

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
