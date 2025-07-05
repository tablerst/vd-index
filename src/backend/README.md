# VD群成员管理系统 - 后端技术文档

## 📋 目录

- [技术栈与架构](#技术栈与架构)
- [整体功能概述](#整体功能概述)
- [目录结构说明](#目录结构说明)
- [核心功能实现](#核心功能实现)
- [数据库设计](#数据库设计)
- [安全机制](#安全机制)
- [API接口文档](#api接口文档)
- [部署与运维](#部署与运维)

## 🛠️ 技术栈与架构

### 核心技术栈

- **Web框架**: FastAPI 0.115+ (异步高性能Python Web框架)
- **数据库**: PostgreSQL + asyncpg (异步数据库驱动)
- **ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic 集成)
- **数据迁移**: Alembic (数据库版本控制)
- **加密**: Cryptography (AES-256-GCM加密)
- **依赖管理**: uv (现代Python包管理器)
- **日志**: Loguru (结构化日志记录)
- **测试**: pytest + pytest-asyncio

### 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 Vue.js   │◄──►│  后端 FastAPI   │◄──►│ PostgreSQL DB   │
│                 │    │                 │    │                 │
│ • API调用       │    │ • 业务逻辑      │    │ • 加密存储      │
│ • 缓存机制      │    │ • 安全处理      │    │ • 代理ID        │
│ • 错误处理      │    │ • 文件管理      │    │ • 头像映射      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 设计原则

1. **安全优先**: QQ号(UIN)全程加密存储，对外仅暴露代理ID
2. **异步架构**: 全异步数据库操作，支持高并发
3. **模块化设计**: 清晰的分层架构，便于维护和扩展
4. **类型安全**: 使用SQLModel实现ORM+Pydantic双重类型验证

## 🎯 整体功能概述

### 主要功能模块

1. **成员管理系统**
   - QQ群成员数据的安全存储与查询
   - 分页列表展示与详情查看
   - 成员统计信息生成

2. **头像服务系统**
   - 基于UIN的头像文件管理
   - 安全的头像访问控制
   - 文件缓存与性能优化

3. **数据导入系统**
   - QQ群JSON数据批量导入
   - 数据验证与错误处理
   - 头像文件自动关联

4. **安全加密系统**
   - AES-256-GCM加密算法
   - 随机盐值生成
   - 密钥管理与轮换

### 核心业务流程

```
数据导入流程:
JSON文件 → 数据验证 → UIN加密 → 数据库存储 → 头像关联

API访问流程:
前端请求 → 路由处理 → 服务层查询 → 数据库检索 → 响应转换 → JSON返回

头像访问流程:
头像请求 → ID验证 → UIN解密 → 文件定位 → 缓存控制 → 文件流返回
```

## 📁 目录结构说明

```
src/backend/
├── alembic/                    # 数据库迁移管理
│   ├── versions/              # 迁移版本文件
│   ├── env.py                 # 迁移环境配置
│   └── script.py.mako         # 迁移脚本模板
├── alembic.ini                # Alembic配置文件
├── api/                       # API路由层
│   ├── __init__.py
│   ├── members.py             # 成员相关API
│   ├── avatars.py             # 头像相关API
│   └── admin.py               # 管理员API
├── core/                      # 核心工具模块
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接(旧版)
│   └── crypto.py              # 加密解密工具
├── services/                  # 基础设施服务层
│   ├── database/              # 数据库服务
│   │   ├── models/           # 数据模型
│   │   │   ├── member/       # 成员模型和CRUD
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py   # 成员模型定义
│   │   │   │   └── crud.py   # 成员CRUD操作
│   │   │   ├── config/       # 配置模型和CRUD
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py   # 配置模型定义
│   │   │   │   └── crud.py   # 配置CRUD操作
│   │   │   ├── activity/     # 活动模型和CRUD
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py   # 活动模型定义
│   │   │   │   └── crud.py   # 活动CRUD操作
│   │   │   └── __init__.py   # 统一导出
│   │   ├── service.py        # 数据库服务类
│   │   ├── factory.py        # 服务工厂
│   │   └── utils.py          # 数据库工具
│   ├── deps.py               # 依赖注入
│   └── schema.py             # 服务注册
├── domain/                    # 业务领域服务层
│   ├── __init__.py
│   ├── member_service.py      # 成员业务逻辑
│   └── avatar_service.py      # 头像业务逻辑
├── schema/                    # API数据模型
│   └── member_schemas.py      # 成员相关Schema
├── scripts/                   # 运维脚本
│   ├── import_group_json.py   # 数据导入脚本
│   ├── verify_import.py       # 导入验证脚本
│   ├── test_crypto.py         # 加密测试脚本
│   ├── debug_avatar.py        # 头像调试脚本
│   ├── quick_avatar_test.py   # 快速测试脚本
│   ├── env_compare.py         # 环境对比脚本
│   ├── copy_avatars.py        # 头像复制脚本
│   └── README.md              # 脚本使用说明
├── test/                      # 测试文件
│   ├── simple_test.py         # 基础功能测试
│   ├── test_database_connection.py  # 数据库连接测试
│   ├── test_database_service.py     # 数据库服务测试
│   └── README.md              # 测试说明文档
├── static/                    # 静态文件
│   ├── avatars/mems/         # 头像文件存储
│   ├── qq_group_*.json       # QQ群数据文件
│   └── index.html            # 前端构建文件
├── data/                      # 数据目录
│   └── avatars/              # 头像数据备份
├── logs/                      # 日志文件
│   ├── app.log               # 应用日志
│   └── error.log             # 错误日志
├── main.py                    # FastAPI应用入口
├── run.py                     # 开发服务器启动脚本
├── pyproject.toml             # 项目配置与依赖
├── uv.lock                    # 依赖锁定文件
├── .env.example               # 环境变量示例
└── README.md                  # 本文档
```

### 关键文件说明

- **main.py**: FastAPI应用主入口，包含应用配置、中间件、路由注册
- **core/config.py**: 统一配置管理，支持环境变量和文件配置
- **core/crypto.py**: 加密解密核心实现，AES-256-GCM算法
- **services/database/service.py**: 异步数据库服务，支持连接池和事务管理
- **services/member_service.py**: 成员业务逻辑，数据转换和业务规则
- **api/**: RESTful API路由定义，请求验证和响应处理

## 🔧 核心功能实现

### 1. 数据库服务架构

#### 异步数据库服务 (DatabaseService)

```python
class DatabaseService:
    """数据库服务类，支持 PostgreSQL + asyncpg + alembic"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=10,
            max_overflow=20
        )

    @asynccontextmanager
    async def with_session(self):
        """数据库会话上下文管理器"""
        async with AsyncSession(self.engine, expire_on_commit=False) as session:
            try:
                yield session
            except SQLAlchemyError as db_exc:
                await session.rollback()
                raise

    async def create_db_and_tables(self) -> None:
        """创建数据库表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
```

#### 依赖注入系统

```python
# services/deps.py
_database_service: Optional[DatabaseService] = None

def set_database_service(service: DatabaseService):
    """设置数据库服务实例"""
    global _database_service
    _database_service = service

async def get_session() -> AsyncSession:
    """获取数据库会话"""
    if not _database_service:
        raise RuntimeError("Database service not initialized")

    async with _database_service.with_session() as session:
        yield session
```

### 2. 安全加密系统

#### AES-256-GCM加密实现

```python
def encrypt_uin(uin: int, salt: str) -> str:
    """使用AES-256-GCM加密UIN"""
    key = derive_key_from_salt(salt)
    nonce = os.urandom(12)  # 96位随机nonce

    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()

    uin_bytes = str(uin).encode('utf-8')
    ciphertext = encryptor.update(uin_bytes) + encryptor.finalize()

    # 返回 nonce + tag + ciphertext 的base64编码
    return base64.b64encode(nonce + encryptor.tag + ciphertext).decode('utf-8')

def decrypt_uin(encrypted_uin: str, salt: str) -> int:
    """解密UIN"""
    key = derive_key_from_salt(salt)
    data = base64.b64decode(encrypted_uin.encode('utf-8'))

    nonce = data[:12]    # 前12字节是nonce
    tag = data[12:28]    # 接下来16字节是tag
    ciphertext = data[28:]  # 剩余是密文

    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return int(plaintext.decode('utf-8'))
```

#### 密钥管理策略

1. **环境变量优先**: `UIN_AES_KEY` 环境变量
2. **文件备用**: `secret_key` 文件自动生成
3. **盐值随机**: 每个成员独立的16字符随机盐值
4. **密钥轮换**: 支持密钥更新而不影响现有数据

### 3. 成员服务业务逻辑

#### 分页查询实现

```python
@staticmethod
async def get_members_paginated(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    base_url: str = ""
) -> Tuple[List[MemberResponse], int]:
    """分页获取成员列表"""
    offset = (page - 1) * page_size

    # 查询成员数据
    statement = select(Member).offset(offset).limit(page_size).order_by(Member.id)
    result = await session.exec(statement)
    members = result.all()

    # 查询总数
    count_statement = select(func.count(Member.id))
    count_result = await session.exec(count_statement)
    total = count_result.one()

    # 转换为响应对象
    member_responses = [
        MemberService.create_member_response(member, base_url)
        for member in members
    ]

    return member_responses, total
```

#### 数据转换与响应构建

```python
@staticmethod
def create_member_response(member: Member, base_url: str = "") -> MemberResponse:
    """创建成员响应对象"""
    avatar_url = f"{base_url}/api/avatar/{member.id}"
    join_date_str = member.join_time.strftime("%Y-%m-%d")
    bio = f"加入于 {join_date_str}"

    return MemberResponse(
        id=member.id,                    # 安全的代理ID
        name=member.display_name,        # 显示名称
        avatar_url=avatar_url,           # 头像URL
        bio=bio,                         # 简介信息
        join_date=join_date_str,         # 入群日期
        role=member.role,                # 群权限
        group_nick=member.group_nick,    # 群昵称
        qq_nick=member.qq_nick           # QQ昵称
    )
```

### 4. 头像服务实现

#### 头像访问控制

```python
@router.get("/avatar/{member_id}")
async def get_avatar(member_id: int, session: AsyncSession = Depends(get_session)):
    """获取头像文件"""
    # 验证成员ID
    if member_id < 1:
        raise HTTPException(status_code=400, detail="无效的成员ID")

    # 根据ID查询成员
    member = await session.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")

    # 解密得到UIN
    uin = decrypt_uin(member.uin_encrypted, member.salt)

    # 构建头像文件路径
    avatar_path = Path(settings.avatar_root) / f"{uin}.webp"

    if not avatar_path.exists():
        raise HTTPException(status_code=404, detail="头像文件不存在")

    # 返回文件流
    return FileResponse(
        path=avatar_path,
        media_type="image/webp",
        headers={
            "Cache-Control": "public, max-age=86400",  # 缓存1天
            "ETag": f'"{member_id}"'
        }
    )
```

## 🗄️ 数据库设计

### 数据模型结构

#### Member 模型 (成员表)

```python
class Member(SQLModel, table=True):
    """群成员模型"""
    __tablename__ = "members"

    # 主键：代理ID（对外公开的安全ID）
    id: Optional[int] = Field(default=None, primary_key=True)

    # 显示名称（群昵称优先，否则QQ昵称）
    display_name: str = Field(max_length=100, index=True)

    # 群昵称和QQ昵称
    group_nick: Optional[str] = Field(default=None, max_length=100)
    qq_nick: Optional[str] = Field(default=None, max_length=100)

    # 加密的UIN（AES-256-GCM加密）
    uin_encrypted: str = Field(max_length=500)

    # 混淆用随机salt (16字节hex)
    salt: str = Field(max_length=32)

    # 群权限：0=群主, 1=管理员, 2=群员
    role: int = Field(default=2)

    # 时间字段
    join_time: datetime                           # 入群时间
    last_speak_time: Optional[datetime] = None    # 最后发言时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 群等级信息
    level_point: Optional[int] = Field(default=0)  # 等级积分
    level_value: Optional[int] = Field(default=1)  # 等级值
    q_age: Optional[int] = Field(default=0)        # Q龄
```

#### Config 模型 (配置表)

```python
class Config(SQLModel, table=True):
    """配置表"""
    __tablename__ = "config"

    key: str = Field(primary_key=True, max_length=100)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 数据安全设计

1. **代理ID机制**: 对外仅暴露自增ID，隐藏真实UIN
2. **加密存储**: UIN使用AES-256-GCM加密，每个成员独立盐值
3. **索引优化**: display_name建立索引，支持快速查询
4. **时间戳**: 记录创建和更新时间，便于数据追踪

### 数据库迁移

使用Alembic进行版本控制：

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述信息"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🌐 API接口文档

### 成员相关接口

#### 获取成员列表

```http
GET /api/members?page=1&page_size=50
```

**响应示例:**
```json
{
  "members": [
    {
      "id": 1,
      "name": "用户昵称",
      "avatar_url": "http://localhost:8000/api/avatar/1",
      "bio": "加入于 2023-01-01",
      "join_date": "2023-01-01",
      "role": 2,
      "group_nick": "群昵称",
      "qq_nick": "QQ昵称"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}
```

#### 获取成员详情

```http
GET /api/members/{member_id}
```

**响应示例:**
```json
{
  "id": 1,
  "name": "用户昵称",
  "avatar_url": "http://localhost:8000/api/avatar/1",
  "bio": "加入于 2023-01-01",
  "join_date": "2023-01-01",
  "role": 2,
  "group_nick": "群昵称",
  "qq_nick": "QQ昵称",
  "level_point": 1000,
  "level_value": 5,
  "q_age": 10,
  "last_speak_time": "2023-12-01"
}
```

### 头像相关接口

#### 获取头像文件

```http
GET /api/avatar/{member_id}
```

**响应**: 返回WebP格式的图片文件流

**缓存控制**:
- `Cache-Control: public, max-age=86400`
- `ETag: "{member_id}"`

#### 检查头像是否存在

```http
HEAD /api/avatar/{member_id}
```

**响应**: HTTP状态码（200存在，404不存在）

### 管理员接口

#### 批量导入成员数据

```http
POST /api/admin/import-json
Content-Type: application/json

{
  "members": [
    {
      "uin": 123456789,
      "card": "群昵称",
      "nick": "QQ昵称",
      "role": 2,
      "join_time": 1640995200,
      "last_speak_time": 1640995200,
      "lv": {"point": 1000, "level": 5},
      "qage": 10
    }
  ]
}
```

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

**常见错误码:**
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 🚀 部署与运维

### 环境配置

#### 环境变量配置 (.env)

```bash
# 数据库配置 (PostgreSQL + asyncpg)
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/vd_index

# 头像文件存储路径
AVATAR_ROOT=./static/avatars/mems

# 加密配置 (可选，如果不设置将使用 secret_key 文件)
UIN_AES_KEY=your-32-character-aes-key-here

# JWT配置 (可选，如果不设置将使用 secret_key 文件)
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# CORS配置
ALLOWED_ORIGINS=["https://your-domain.com"]
ALLOWED_HOSTS=["your-domain.com"]
```

### 开发环境启动

```bash
# 1. 安装依赖
cd src/backend
uv sync

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置正确的数据库连接

# 3. 运行数据库迁移
uv run alembic upgrade head

# 4. 启动开发服务器
uv run python main.py
# 或者
uv run python run.py
```

### 生产环境部署

#### 使用 Gunicorn + Uvicorn

```bash
# 1. 安装生产依赖
uv sync

# 2. 配置生产环境变量
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"
export DEBUG=false
export AVATAR_ROOT="/var/www/avatars"

# 3. 运行数据库迁移
uv run alembic upgrade head

# 4. 启动生产服务器
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

#### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装 uv
RUN pip install uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --frozen

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### 数据导入

#### 导入QQ群成员数据

```bash
# 导入JSON文件
cd src/backend
uv run python scripts/import_group_json.py static/qq_group_members.json

# 验证导入结果
uv run python scripts/verify_import.py

# 测试加密解密
uv run python scripts/test_crypto.py
```

### 运维脚本

#### 调试工具

```bash
# 快速测试基本功能
uv run python scripts/quick_avatar_test.py

# 详细调试信息
uv run python scripts/debug_avatar.py

# 环境对比
uv run python scripts/env_compare.py
```

#### 日志管理

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 日志轮换 (建议使用 logrotate)
logrotate /etc/logrotate.d/vd-backend
```

### 性能监控

#### 关键指标

1. **数据库连接池**: 监控连接数和等待时间
2. **API响应时间**: 特别关注头像接口性能
3. **内存使用**: 监控异步任务内存泄漏
4. **磁盘空间**: 监控头像文件存储空间

#### 性能优化建议

1. **数据库优化**:
   - 为 display_name 建立索引
   - 定期分析查询性能
   - 考虑读写分离

2. **缓存策略**:
   - 头像文件使用 CDN
   - API响应使用 Redis 缓存
   - 数据库查询结果缓存

3. **文件存储**:
   - 头像文件使用对象存储
   - 定期清理无效文件
   - 实现文件压缩

### 安全建议

1. **密钥管理**: 定期轮换加密密钥
2. **访问控制**: 实现API访问频率限制
3. **日志审计**: 记录敏感操作日志
4. **数据备份**: 定期备份数据库和头像文件
5. **HTTPS**: 生产环境必须使用HTTPS

---

## 📞 技术支持

如有问题，请查看：
1. [调试指南](scripts/DEBUG_GUIDE.md)
2. [测试文档](test/README.md)
3. [脚本说明](scripts/README.md)

或联系开发团队获取技术支持。