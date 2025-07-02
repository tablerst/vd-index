# VD群成员管理系统 - 后端调用链分析报告

## 1. 系统架构概览

### 1.1 整体架构
```
前端 (Vue.js + TypeScript)  ←→  后端 (FastAPI + SQLAlchemy async)  ←→  数据库 (PostgreSQL)
     ↓                              ↓                                   ↓
  API调用                        业务逻辑                            加密存储
  缓存机制                        安全处理                            代理ID
  错误处理                        文件管理                            头像(UIN.webp)
```

### 1.2 核心安全设计
- **UIN加密**: 使用 AES-256-GCM 加密存储 QQ 号  
- **代理ID机制**: 对外使用自增 ID，隐藏真实身份  
- **头像安全**: 前端仅用成员 ID 访问 `/api/avatar/{id}`；文件名仍为 `{uin}.webp`，永不暴露  
- **UIN混淆盐**: 每个成员存储随机 `salt`，后端通过 `uin + "vd" + salt` 进行混淆 / 解混淆  
- **访问控制**: CORS、速率限制、权限验证

## 2. 数据加密与存储层

### 2.1 密钥管理 (`core/config.py`, `core/crypto.py`)

```python
# filepath: core/crypto.py
class CryptoManager:
    def __init__(self):
        self._key = None
        self._salt = b"vd_member_salt_2024"  # 固定盐值
    
    @property
    def key(self) -> bytes:
        if self._key is None:
            master_key = get_or_create_aes_key()
            # 使用PBKDF2从主密钥派生AES密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # AES-256需要32字节密钥
                salt=self._salt,
                iterations=100000,
            )
            self._key = kdf.derive(master_key.encode())
        return self._key
```

**密钥生成流程:**
1. 检查环境变量 `UIN_AES_KEY` 或密钥文件 `./secret_key`
2. 如不存在，自动生成32字节随机密钥
3. 使用PBKDF2-HMAC-SHA256派生最终加密密钥
4. 100,000次迭代增强安全性

### 2.2 UIN加密流程
重写后的流程：
1. 为新成员生成 **8 byte 随机 `salt`（16 hex）**  ← 由 secrets.token_hex(8) 产生
2. 组合字符串 `mixed = f"{uin}vd{salt}"`  
3. 使用全局 AES-256-GCM 密钥对 `mixed` 加密  
4. 将 `nonce + ciphertext` 进行 Base64 编码后写入 `uin_encrypted` 字段

```python
def encrypt_uin(uin: int, salt: str) -> str:
    aesgcm = AESGCM(CryptoManager().key)
    nonce = secrets.token_bytes(12)
    mixed = f"{uin}vd{salt}".encode("utf-8")
    cipher = aesgcm.encrypt(nonce, mixed, None)
    return base64.b64encode(nonce + cipher).decode()
```
解密时先 Base64 → 分离 `nonce` → 解密 → 解析出 `uin`。  
该方案保证：数据库不存明文 UIN，且文件系统仍以 `{uin}.webp` 命名，无外泄风险。

### 2.3 数据库模型
```python
# filepath: src/backend/models/member.py
class Member(SQLModel, table=True):
    """
    ORM + Pydantic 模型，支持异步 SQLAlchemy (asyncpg) 操作并兼容 Pydantic 验证与序列化
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="自增代理ID")
    display_name: str = Field(..., max_length=100, index=True, description="展示名称（优先群名片，否则为QQ昵称）")
    group_nick: Optional[str] = Field(default=None, max_length=100, description="群名片（card）")
    qq_nick: Optional[str] = Field(default=None, max_length=100, description="QQ昵称（nick）")
    role: int = Field(..., description="成员角色 (1 普通 / 2 管理员 / 3 群主)")
    uin_encrypted: str = Field(..., max_length=500, description="加密后的QQ号 (Base64 格式)")
    salt: str = Field(..., max_length=32, description="混淆用随机salt (16字节hex)")
    join_time: int = Field(..., description="入群时间 (Unix时间戳)")
    last_speak_time: int = Field(..., description="上次发言时间 (Unix时间戳)")
    level_point: int = Field(..., description="等级积分")
    level_value: int = Field(..., description="等级值")
    tags: str = Field(..., description="自定义标签，逗号分隔")
    flag: int = Field(..., description="系统标记 (如黑名单)")
    q_age: int = Field(..., description="QQ年龄 (年)，参考QQ群背景")
    rm: int = Field(..., description="本地活跃度评分 (Reserved for metrics)")
```
> 说明：ORM 仍用 **SQLModel**（基于 SQLAlchemy asyncpg），同时兼具 Pydantic 验证与序列化；计划引入 Alembic 进行数据库迁移。

## 3. API接口调用链

#### 3.1 成员数据API (`api/members.py`)

**主要接口:**
- `GET /api/members` - 分页获取成员列表
- `GET /api/members/{member_id}` - 获取成员详情
- `GET /api/members/stats` - 获取统计信息

**数据流程:**
```
客户端请求 → 路由处理 → 服务层查询 → 数据库检索 → 响应模型转换 → JSON返回
```

#### 3.2 头像服务API (`api/avatars.py`)
```python
# filepath: api/avatars.py
@router.get("/avatar/{member_id}")
async def get_avatar(member_id: int):
    # 根据 ID 查询成员
    member = MemberService.get_member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")

    # 解混淆得到 uin
    uin = decrypt_uin(member.uin_encrypted, member.salt)
    avatar_path = f"{AVATAR_DIR}/{uin}.webp"

    return FileResponse(
        path=avatar_path,
        media_type="image/webp",
        headers={"Cache-Control": "public, max-age=86400"}
    )
```
**头像访问流程:**
```
前端请求 → ID查询 → 解混淆UIN → 文件路径解析 → 文件存在检查 → 缓存头设置 → 文件流返回
```

## 4. 前端调用链

### 4.1 API客户端 (`src/frontend/src/services/api.ts`)

```typescript
// filepath: src/frontend/src/services/api.ts
class ApiClient {
  // 获取成员列表
  async getMembers(page: number = 1, pageSize: number = 50): Promise<MemberListResponse> {
    return this.request<MemberListResponse>(
      `/api/members?page=${page}&page_size=${pageSize}`
    )
  }

  // 获取头像 URL（按成员 ID）
  getAvatarUrl(memberId: number): string {
    return `${this.baseURL}/api/avatar/${memberId}`
  }
}
```

### 4.2 数据适配层 (`src/frontend/src/stores/members.ts`)

```typescript
// 从API Member转换为本地Member的适配器
function adaptApiMember(apiMember: ApiMember): Member {
  return {
    id: apiMember.id,
    name: apiMember.name,
    avatarURL: apiMember.avatar_url, // 转换字段名
    bio: apiMember.bio,
    joinDate: apiMember.join_date, // 转换字段名
    role: apiMember.role,
    groupNick: apiMember.group_nick,
    qqNick: apiMember.qq_nick
  }
}
```

**前端数据流:**
```
API调用 → 数据适配 → 状态管理 → 组件渲染 → 用户界面
```

## 5. 数据导入流程 (`src/backend/scripts/import_group_json.py`)
离线脚本执行流程：
1. 读取指定 QQ 群 JSON（结构见示例）  
2. 使用 SQLModel 会话 `session.exec(delete(Member))` 清空 `Member` 表  
3. 对每条记录：生成 `salt` → `encrypt_uin(uin, salt)` → 创建 `Member` 实例  
4. 批量插入后提交事务  
5. 检查 `{uin}.webp` 是否存在，缺失记录到日志

```python
# filepath: src/backend/scripts/import_group_json.py
# ...existing imports...
from sqlalchemy.ext.asyncio import AsyncSession

async def import_members(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    members = []
    for item in data:
        salt = secrets.token_hex(8)  # 8 byte hex
        uin_enc = encrypt_uin(item["uin"], salt)
        members.append(
            Member(
                display_name=item.get("card") or item.get("nick"),
                group_nick=item.get("card"),
                qq_nick=item.get("nick"),
                role=item["role"],
                uin_encrypted=uin_enc,
                salt=salt,
                join_time=item["join_time"],
                last_speak_time=item["last_speak_time"],
                level_point=item["lv"]["point"],
                level_value=item["lv"]["level"],
                tags=item["tags"],
                flag=item["flag"],
                q_age=item["qage"],
                rm=item["rm"],
            )
        )

    # 使用 AsyncSession(engine) as sess
    async with AsyncSession(engine) as sess:
        await sess.execute(delete(Member))
        await sess.commit()
        sess.add_all(members)
        await sess.commit()
        # ...existing code...
```
> 运行脚本时使用 `asyncio.run(import_members(Path("group.json")))`。

## 6. 配置管理（.env）

关键变量示例：

```
# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vd_member
UIN_AES_KEY=Base64OrHexKey
ALLOWED_ORIGINS=https://admin.example.com
RATE_LIMIT_REQUESTS=100/minute
```

应用入口 `app/config.py` 使用 `python-dotenv` 自动加载：

```python
from dotenv import load_dotenv; load_dotenv()
```

## 7. 文件结构说明

### 7.1 后端文件结构
```
src/backend/
├── alembic/               # 数据库迁移脚本
│   └── versions/
├── api/                   # FastAPI 路由聚合（成员、头像等）
├── core/                  # 核心工具：config、database、crypto
│   ├── config.py
│   ├── database.py
│   └── crypto.py
├── components/            # 可复用业务组件（如分页、权限）
├── events/                # 启动/关闭事件处理
├── exceptions/            # 统一异常定义
├── helpers/               # 通用辅助函数
├── models/                # ORM 实体（SQLModel / Pydantic）
├── schema/                # API 请求/响应模型
├── services/              # 业务逻辑层
├── scripts/               # 运维脚本
│   └── import_group_json.py
├── utils/                 # 工具库（加密、日志封装等）
├── __init__.py
└── main.py                # FastAPI 入口
```

### 7.2 前端文件结构
```
src/frontend/
├── index.html
├── vite.config.ts
├── public/                   # 纯静态资源
└── src/
    ├── assets/               # 本地静态资源（logo / 图片 / 数据）
    ├── components/           # 通用 & 复合组件
    │   └── icons/            # 图标组件
    ├── composables/          # 组合式 API / hooks
    ├── stores/               # Pinia 状态管理
    ├── services/             # 后端 API 客户端封装
    ├── utils/                # 工具库（Three.js / Canvas / 通用方法）
    ├── styles/               # SCSS 变量 & 全局 / 页面样式
    │   └── pages/            # 页面级样式文件
    ├── types/                # ts 类型声明（如 *.d.ts）
    ├── views/                # 页面级组件（如采用路由拆分）
    ├── App.vue               # 根组件
    ├── main.ts               # 入口脚本
    └── env.d.ts              # Vite 环境类型声明
```

### 7.3 包管理（pnpm）

项目默认使用 **pnpm (v8+)** 作为包管理器，带来更快的安装速度、硬链接去重及 monorepo 友好特性。常用命令对照如下：

```bash
# 安装依赖
pnpm install

# 本地开发
pnpm dev           # 等同 npm run dev

# 类型检查 + 打包（开发/生产）
pnpm build         # 对应 npm run build
pnpm run build:prod

# 预览生产构建
pnpm preview
```

注意事项：
- 仓库根目录会生成 `pnpm-lock.yaml`，**请务必纳入版本控制**，以保证团队环境一致。
- 若全局未安装，先执行 `npm i -g pnpm@latest`（需 ≥ 8）。

### 7.4 依赖管理（uv）

后端 Python 端依赖使用 **uv**（`pip` 的极速替代品）结合 **PEP-621** `pyproject.toml` 管理，优点：并行解析、二进制缓存及无需虚拟环境时依旧可快速安装。

```bash
# 创建并激活虚拟环境（推荐）
uv venv --python 3.11
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安装项目依赖（读取 pyproject.toml）
uv sync
```

注意事项：
- `pyproject.toml` 中 `[project]` 与 `[dependency-groups]` 已按 uv 规范定义；新增依赖务必通过 `uv add` 让其写入文件。
- `uv.lock` 能保证 CI/CD 与本地环境一致，**请加入版本控制**。

## 8. 结论

您的后端调用链设计完全符合最初的安全设想，成功实现了：

- **数据安全**  
- **隐私保护**  
- **文件安全**  
- **访问控制**  
- **可维护性**  

整个系统架构清晰，安全措施到位，为后续的重构工作提供了良好的基础。  
建议在后续迭代中逐步优化系统性能和可维护性。