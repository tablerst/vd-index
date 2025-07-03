"""
FastAPI主应用
"""
import time
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
from api import members, avatars, admin


# 速率限制器
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 启动后端服务...")

    # 初始化数据库服务
    factory = DatabaseServiceFactory()
    db_service = factory.create(settings.database_url)
    set_database_service(db_service)

    # 创建数据库和表
    await db_service.create_db_and_tables()
    print("✅ 数据库初始化完成")

    # 确保必要的目录存在
    from pathlib import Path
    Path(settings.avatar_root).mkdir(parents=True, exist_ok=True)
    Path("./data").mkdir(parents=True, exist_ok=True)
    print("✅ 目录结构初始化完成")

    yield

    # 关闭时执行
    print("🛑 关闭后端服务...")
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
app.include_router(members.router)
app.include_router(avatars.router)
app.include_router(admin.router)


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
