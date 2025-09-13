# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Table of Contents

- Commands
- Architecture overview
- Important project rules and notes
- Common workflows
- Frontend module details
  - services/api.ts（HTTP 客户端与业务 API 门面）
  - services/daily.ts（Daily Posts 独立 API）
  - router（index.ts 与 guards.ts）
  - stores/auth.ts（认证状态：Pinia Store）
- Backend module details
  - 应用启动与装配（main.py, run.py, api/router.py, services/deps.py）
  - 配置服务（services/config/*）
  - 认证服务（services/auth/*）
  - 数据库与模型（services/database/*, alembic）
  - API 路由集合（api/v1/*, api/router.py）
  - 缓存服务（services/cache/*）
  - 加密服务（services/crypto/*）
  - Schema（src/backend/schema/*.py）
  - 领域层（domain/member_service.py）
  - 工具模块（utils/*）

## Key Takeaways

- Frontend
  - 认证全链路：`utils/token.ts` 负责 Token 刷新与请求头注入；`router/guards.ts` 与 `stores/auth.ts` 协同保证私有路由访问控制；
  - API 门面：`services/api.ts` 做领域 API 封装与 401 重试；`services/daily.ts` 单独维护日常流与评论，支持开发态 Mock；
  - 类型严格：前端 API/Store 的入参/出参均有 TypeScript 类型定义；

- Backend
  - 生命周期装配：`main.py` 在 lifespan 中完成 config/cache/crypto/db/auth 的注入；生产模式挂载 `/` 静态前端；
  - 安全与规范：JWT 鉴权、CORS/TrustedHost、统一异常响应、限流（slowapi）、健康检查；
  - 数据与时间：SQLModel 统一北京时区 naive 存储；Schema 层统一 ISO 字符串输出；
  - 性能与复用：全局缓存服务支持 per-key TTL、批量操作与装饰器；成员读写路径与统计均整合缓存；
  - 领域职责：成员导入 Upsert/退群对账集中在 `domain/member_service.py`；头像下载与 QQ 抓取解耦到 `utils/`；
  - 配置驱动：.env 控制数据库/密钥/CORS/缓存 TTL/速率限制/SUPER_USER_* 等，生产建议使用 Alembic 迁移。

## Commands

Frontend (Vite + Vue 3, TypeScript, Pinia):
- Install deps (pnpm):
  - cd src/frontend && pnpm install
- Dev server:
  - cd src/frontend && pnpm dev
- Typecheck + build:
  - cd src/frontend && pnpm build
- Preview built app:
  - cd src/frontend && pnpm preview

Backend (FastAPI + SQLModel, uv as package manager):
- Install deps (uses uv with pyproject.toml/uv.lock):
  - cd src/backend && uv sync
- Run DB migrations (alembic):
  - cd src/backend && uv run alembic upgrade head
- Start dev server (reload respects DEBUG in .env):
  - cd src/backend && uv run python run.py
  - or: cd src/backend && uv run python main.py
- Start prod server (Gunicorn + Uvicorn worker):
  - cd src/backend && uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

Testing:
- Backend tests (pytest):
  - cd src/backend && uv run pytest
  - Single test file:
  - cd src/backend && uv run pytest tests/test_jsonb_models.py -q

Linting/formatting:
- Python (pylint, black available in dev group):
  - cd src/backend && uv run black .
  - cd src/backend && uv run pylint src backend
- TypeScript: no explicit lint script; strict TS config is enforced via vue-tsc during build.

Environment:
- Frontend env files in src/frontend (.env.development, .env.production). Key: VITE_API_BASE_URL.
- Backend env in src/backend/.env (see .env.example). Key settings: DATABASE_URL, AVATAR_ROOT, JWT_*, HOST/PORT, DEBUG, CORS, CACHE_*, SUPER_USER_*.

## Architecture overview

Monorepo with a Vue 3 frontend and FastAPI backend.

Frontend:
- Stack: Vite, Vue 3 (SFC), TypeScript, Pinia, Vue Router, TailwindCSS.
- Entry: src/frontend/src/main.ts creates app, installs Pinia and router.
- Routing: src/frontend/src/router/index.ts defines public pages and /settings admin area; guards in src/frontend/src/router/guards.ts enforce auth/roles and set document title.
- State: src/frontend/src/stores/auth.ts manages JWT-based auth using utils/token.ts (localStorage, auto refresh via /api/v1/auth/refresh) and integrates with services/api.ts.
- Services: src/frontend/src/services/api.ts wraps fetch with RequestInterceptor/TokenRefreshManager and provides typed APIs (members, activities, comments, configs). Daily posts feature is isolated in src/frontend/src/services/daily.ts with optional mock data (VITE_DAILY_USE_MOCK).
- Build/config: vite.config.ts sets alias @ -> src, dev server proxy /api to localhost:8000, production minify via terser. Tailwind and PostCSS configured. Strict TS via tsconfig.app.json.

Backend:
- Stack: FastAPI, SQLModel/SQLAlchemy async, Alembic, Uvicorn/Gunicorn, pydantic-settings, slowapi, loguru.
- App entry: src/backend/main.py creates FastAPI app with lifespan startup wiring services, CORS/trusted hosts, exception handlers, health endpoint, and conditional static serving of built frontend under src/backend/static in production.
- Services layer under src/backend/services:
  - database (engine/session, models, alembic migrations, utils),
  - auth (JWT, user management),
  - config (settings via .env/pydantic-settings). Details:
    - services/config/service.py: Settings (pydantic-settings) loads .env; allowed_origins/hosts via env; provides ensure_secret_key() to create/read secret_key file (600 perms) and get_or_create_aes_key() preferring UIN_AES_KEY env, else secret_key file.
    - services/config/factory.py: simple factory returning ConfigService(); services/deps.py exposes set_config_service/get_config_service.
  - crypto (AES utilities),
  - cache.
- API routers under src/backend/api/v1: members, activities, comments, configs, daily, avatars, users_bind, admin. Main router assembled in api/router.py.
- Data models organized per domain: member, activity, config, comment, daily_post, daily_post_comment with corresponding CRUD modules.
- Environment-driven behavior: DEBUG toggles docs and static mounting; DATABASE_URL for PostgreSQL via asyncpg; SUPER_USER_* used on startup to ensure an admin account exists; AVATAR_ROOT for avatar storage.

Frontend-backend integration:
- During development, Vite proxies /api to localhost:8000 (vite.config.ts). Frontend uses VITE_API_BASE_URL or defaults to http://localhost:8000 in dev.
- In production, build frontend (outDir=dist) and deploy its assets to src/backend/static to be served by FastAPI at "/" when DEBUG=false.

## Important project rules and notes

- Cursor rules are present under .cursor/rules/. Key items: always use task list planning; comments in markdown may be Chinese but code comments should be English; avoid executing tests during code writing in complex setups, keep static checks passing.
- Git ignores sensitive data and generated assets (see root .gitignore). Do not commit backend .env, secret_key, avatar data, or built static files.

## Common workflows

Local development:
1) Backend: create src/backend/.env from .env.example and set DATABASE_URL (PostgreSQL). Then:
   - uv sync
   - uv run alembic upgrade head
   - uv run python run.py
2) Frontend:
   - pnpm install
   - pnpm dev (uses VITE_API_BASE_URL from .env.development)

Build and serve production:
1) Frontend: cd src/frontend && pnpm build
2) Copy dist/ to src/backend/static (or serve separately via CDN). When DEBUG=false, FastAPI serves index.html at root.
3) Backend: uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

Running a single backend test:
- cd src/backend && uv run pytest tests/test_time_beijing.py -q

## Frontend module details

### services/api.ts（HTTP 客户端与业务 API 门面）

- 核心职责：
  - 统一封装 HTTP 请求、鉴权头注入与 401 重试；
  - 按领域提供强类型 API 方法（成员/活动/评论/配置/缓存/健康检查）；
  - 提供便捷门面 `memberApi`/`activityApi`/`commentApi`/`configApi` 与新系统 `actApi`；
  - 提供通用错误与重试、轻量内存缓存工具。

- 基础配置：
  - `API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (PROD ? '' : 'http://localhost:8000')`；
  - 生产相对路径，开发走完整 URL（配合 Vite 代理）。

- 请求链路：
  1) 发起前：`TokenRefreshManager.autoRefreshToken()` 预刷新；
  2) 注入头：`RequestInterceptor.addAuthHeader` 将 `Authorization: Bearer <token>` 写入；
  3) `fetch(url, config)` 执行；
  4) 401：交由 `RequestInterceptor.handleAuthError({ response, config:{... , url} })` 尝试刷新并回填新头；
     - 刷新成功返回重试用 config，再次 `fetch`；失败且曾有登录态则跳转 `/login`。

- 认证接口：
  - `login({ username, password })`：使用 `FormData`，不显式设置 `Content-Type`；
  - `register({ username, password })`：`application/json`；
  - `changePassword({ old_password, new_password })`；
  - `getCurrentUser()`；`logout()`（占位，当前前端直接清本地态）。
  - 为 `stores/auth.ts` 提供简化门面 `api.post/get` 仅覆盖 `/auth/login`、`/auth/register`、`/auth/me`。

- 成员（members）：
  - 查询分页/详情：`getMembers(page,size)`、`getMemberDetail(id)`；
  - 变更：`createMember`/`updateMember`/`deleteMember`；
  - 导入：文件 `adminImportFile(file)`、直接 JSON `adminImportJson(mems)`、QQ 参数导入 `adminImportFromQQ(params)`、批量 Upsert `membersImport({members})`；
  - 统计与头像：`getMemberStats()`、`refreshAllAvatars()`、`getAvatarUrl(memberId)`；
  - 便捷集：`memberApi` 提供 `getAllMembers()`（自动并发拉全量）、`extractMemberId(avatarUrl)` 等。

- 活动（星历旧域 star_calendar）：
  - 列表/统计/详情：`getActivities`、`getActivityStats`、`getActivity`；
  - CRUD：`createActivity`、`updateActivity`、`deleteActivity`；
  - 便捷集：`activityApi` 提供分页、全量与日期格式化工具。

- 活动（新系统 activities）：
  - 端点：`activitiesList(status,page,size)`、`activityDetail`、`activityRanking(top,withSelf)`、`activityOptions(query,cursor,size)`、`activityVote`、`activityRevoke`、`activityCreate`；
  - 类型：`ActActivity`/`ActVoteOption`/`ActRankingEntry`/`ActVoteSubmit`；
  - 门面：`actApi` 直接复用 `apiClient`，对新系统做轻封装（默认创建 `type: 'vote'`）。

- 评论（comments）：
  - 针对 “成员评论” 模块：列表 `getMemberComments`、`createComment`、点赞/点踩、删除（管理员）、统计；
  - 门面 `commentApi` 附带：相对时间格式化、内容校验（长度/非空）。

- 配置（configs）：
  - 列表/详情/按 key：`getConfigs`、`getConfig(id)`、`getConfigByKey(key)`；
  - CRUD：`createConfig`、`updateConfig`、`deleteConfig`；
  - 门面 `configApi`：
    - 值校验（number/boolean/json/string），
    - 展示格式化（布尔/JSON 美化），
    - 实值解析（将字符串转换为对应类型）。

- 缓存/健康检查（后端）：
  - `getCacheStats()`、`clearCache()`、`deleteCacheKey(key)`；
  - `healthCheck()`。

- 错误与稳定性：
  - `ApiError`：错误类型（当前内部 `request` 直接抛 `Error(detail || HTTP ...)`，`ApiError` 作为对外类型保留）；
  - `withRetry(fn,maxRetries=3,delay=1000)`：指数退避；
  - 轻量缓存：`ApiCache` + `cachedApiCall(key, apiCall, ttl=5min)`，适合只读接口做按需缓存（默认不全局启用）。

- 依赖与协作：
  - 强依赖 `utils/token.ts`：`TokenRefreshManager`（串行刷新、`/api/v1/auth/refresh`）与 `RequestInterceptor`（401 处理、跳转控制）；
  - 由 `stores/auth.ts` 消费简化 `api` 门面，登录态写入 `TokenManager`，并由 `TokenWatcher` 定时自检；
  - 路由守卫 `router/guards.ts` 访问 `/auth/me` 校验用户态。

- 与 daily 子域的边界：
  - “日常内容流” 独立在 `services/daily.ts`，避免 `api.ts` 体积/领域漂移；
  - 共享相同的鉴权拦截/自动刷新逻辑；
  - 开发态支持 Mock：`VITE_DAILY_USE_MOCK === 'true'` 时本地生成多样内容/图片。

### services/daily.ts（Daily Posts 独立 API）

### router（index.ts 与 guards.ts）

### stores/auth.ts（认证状态：Pinia Store）

- 状态切片：`user`、`token`、`isLoading`、`error`；`isAuthenticated` 为派生。
- 初始化：从 `TokenManager` 读本地态，若 token 未过期则启动 `TokenWatcher` 定时自检。
- 行为：
  - `login(credentials)`：调用 `api.post('/api/v1/auth/login')`，`setAuth()` 写入本地与状态，成功后跳转到 `query.redirect || '/settings'`；
  - `register(credentials)`：同登录，返回布尔成功标记；
  - `logout()`：清空本地与状态并跳转首页；
  - `validateToken()`：如本地 token 将请求 `/api/v1/auth/me` 更新 `user`，过期或失败则清态。
- 工具：
  - `TokenManager`：localStorage 的 `access_token`/`refresh_token`/`user` 管理、过期判定、JWT 解析；
  - `TokenWatcher`：`setInterval` 每 60s 调 `TokenRefreshManager.autoRefreshToken()`。
- 与路由守卫协作：守卫在需要鉴权的路由上优先调用 `validateToken()` 保证刷新后的用户态有效。

- 路由结构：
  - 公共页：`/` 首页、`/badge-preview` 徽章预览、`/daily` 列表、`/daily/:id` 详情、`/login` 登录；
  - 管理区：`/settings` 布局，子路由：`dashboard`/`members`/`activities`/`configs`，均设 `requiresAuth: true`；`configs` 额外要求 `roles: ['admin']`。

- 前置守卫：
  - 若路由链任一记录含 `requiresAuth`：
    - 已认证：继续；
    - 未认证但本地有 token：调用 `authStore.validateToken()`（内部会请求 `/api/v1/auth/me`）；
    - 失败/无 token：重定向 `/login?redirect=<to.fullPath>`。
  - 角色校验：若 `to.meta.roles` 存在，则从 `authStore.user.role` 匹配，不通过则重定向首页并附加 `insufficient_permissions`。

- 后置钩子：
  - 设置文档标题为：`<meta.title> - VD群管理系统`；
  - 开发阶段输出路由切换日志。

- 权限辅助：
  - `hasPermission(permission)`：管理员 `admin` 拥有 `*`；其他角色基于内置 `rolePermissions` 映射；
  - `hasRole(role)`、`isAdmin()`、`isModerator()` 简化判定；
  - 扩展 `RouteMeta` 类型，声明 `requiresAuth`/`roles`/`permissions`/`title`/`icon` 等。

- 职责：每日帖子与评论的列表/详情/创建/更新/删除、图片上传、最近评论。
- 关键点：
  - 统一 `request()` 前置刷新与头注入；
  - Mock 开关 `VITE_DAILY_USE_MOCK`（仅开发），自动生成 12—20 条多样化数据；
  - 评论返回结构包含 `top_comments` 与 `children_map`，便于前端合并渲染树；
  - 图片上传使用 `FormData`，不手动设置 `Content-Type`。

- 端点映射：
  - 列表/详情：`GET /api/v1/daily/posts`，`GET /api/v1/daily/posts/:id`；
  - 写操作：`POST /api/v1/daily/posts`，`PATCH /api/v1/daily/posts/:id`，`DELETE /api/v1/daily/posts/:id`；
  - 上传：`POST /api/v1/daily/upload` 多文件（字段名 `images`）；
  - 评论：
    - 列表：`GET /api/v1/daily/posts/:postId/comments?page=&page_size=`；
    - 新增：`POST /api/v1/daily/posts/:postId/comments { content, parent_id? }`；
    - 点赞/点踩：`PUT /api/v1/daily/comments/:id/(like|dislike)`；
    - 删除：`DELETE /api/v1/daily/comments/:id`；
    - 最近：`GET /api/v1/daily/comments/recent?limit=`。

- 类型：`DailyPostItem`、`DailyPostListResponse`、`DailyCommentItem`、`DailyCommentListResponse`、`UploadImagesResponse`。

## Backend module details

### 应用启动与装配（main.py, run.py, api/router.py, services/deps.py）

- 启动入口：
  - `src/backend/run.py`：读取配置后以 `uvicorn.run('main:app', host, port, reload=settings.debug)` 启动；
  - `src/backend/main.py`：支持 `python main.py` 直接运行，参数同上。

- 应用初始化（main.py）：
  - 日志：日志目录放置在项目根的 `logs/`（相对 main.py 为 `../../logs`），避免触发热重载；根 logger + 控制台 + 文件 + 错误文件，收敛第三方 logger 等级；
  - 限流：`slowapi`，以 `Limiter(get_remote_address)` 配置 `app.state.limiter` 并注册 `_rate_limit_exceeded_handler`；
  - CORS/可信主机：`CORSMiddleware` 开放 PATCH/OPTIONS；生产启用 `TrustedHostMiddleware` 并读取白名单；
  - 全局异常：统一包装 `HTTPException` 和通用异常，DEBUG 模式返回 traceback；
  - 文档与健康：`/docs`/`/redoc` 仅在 DEBUG，`/health` 始终可用；
  - 中间件：注入 `X-Process-Time` 请求耗时头。

- Lifespan（启动/停止）：
  - 启动：
    1) `ConfigService` 初始化并注入；
    2) `CacheService`、`CryptoService`、`DatabaseService`、`AuthService` 依次创建并注入；
    3) `await db_service.create_db_and_tables()`；
    4) 确保资源目录：`settings.avatar_root` 与 `./data`；
    5) `ensure_admin_user_exists()`：若无 admin，则由 `.env` 的 `SUPER_USER_*` 创建；
  - 停止：调用 `db_service.teardown()` 释放连接等资源。

- 路由聚合（api/router.py）：
  - 以 `v1_router`（前缀 `/api/v1`）注册各域：`auth/setup/users_bind/members/avatars/admin/activities/configs/cache/comments/daily/daily_comments`；
  - 顺序注意：先 `users_bind` 再 `members`，避免 `members/{id}` 抢占 `members/bindable`；
  - `main_router` 汇总版本，`app.include_router(main_router)`。

- 静态资源（生产）：
  - 若存在 `src/backend/static`：
    - 生产：挂载到 `/`（`html=True`），服务前端打包产物；
    - 开发：可选挂载到 `/static` 便于调试；
  - 若生产但缺少静态目录，会打印警告提示先构建前端。

- 依赖注入（services/deps.py）：
  - 模块级单例：`set_/get_` 方法管理 `database/auth/config/crypto/cache` 服务；
  - 访问前需由 lifespan 完成 `set_*`，否则 `get_*` 抛错提示初始化顺序；
  - 会话：`get_session()` 生成器用于 FastAPI 依赖；`session_scope()` 提供事务封装（提交/回滚）。

### 配置服务（services/config/*）

- Settings：
  - 使用 `pydantic-settings` 从 `.env` 读取；键位覆盖数据库、头像目录、JWT（secret/alg/有效期）、CORS（`ALLOWED_ORIGINS`/`ALLOWED_HOSTS`）、缓存 TTL、速率限制、服务端 host/port、`DEBUG` 与 `SUPER_USER_*` 等；
  - 默认允许来源含 Vite 本地端口与生产域 `tomo-loop.icu`。

- ConfigService：
  - `get_settings()` 懒加载 `Settings()` 并缓存；
  - `ensure_secret_key()`：确保 `settings.secret_key_file` 存在；若缺失则生成 `secrets.token_urlsafe(32)` 写入并 chmod 600；
  - `get_or_create_aes_key()`：优先环境变量 `UIN_AES_KEY`，否则回退到 `ensure_secret_key()`；用于成员 UIN 加解密等。

- 工厂：`ConfigServiceFactory.create()` 简单返回新实例；在 `main.py` 的 lifespan 与 `run.py` 中统一使用。

### 认证服务（services/auth/*）

- AuthService：
  - 密钥/算法/有效期来源于 `Settings`（.env）；
  - 密码：`passlib` 的 `bcrypt` 哈希与校验；
  - JWT：`python-jose` 生成/校验，`sub` 存用户名，`exp` 到期；
  - 提供 `create_access_token(data, expires_delta?)` 与 `verify_token(token)`。

- utils：
  - OAuth2：`OAuth2PasswordBearer(tokenUrl='api/v1/auth/login', auto_error=False)`；
  - 依赖：`get_current_user` 从 `Authorization` 提取 token，校验并查询用户；`get_current_active_user` 检查 `is_active`；`get_admin_user`/`require_admin` 断言角色为 `admin`；
  - 管理员创建：`create_super_user(session, auth_service, username, password, email?)`，用于启动时的管理员引导。

- 工厂：`AuthServiceFactory.create()` 读取全局 `ConfigService`，注入 `Settings` 构建实例。

### 数据库与模型（services/database/*, alembic）

- DatabaseService：
  - 方言归一：将 `postgres://`/`postgresql://` 统一为 `postgresql+asyncpg://`；
  - 引擎：`create_async_engine(..., pool_size=10, max_overflow=20, json_serializer=orjson_dumps_compact)`；
  - 会话：`with_session()` 提供 `AsyncSession(expire_on_commit=False)` 上下文；
  - 表：`create_db_and_tables()` 基于 `SQLModel.metadata.create_all`；
  - 迁移：`run_migrations()` 配置 `alembic` 脚本路径与 `sqlalchemy.url` 并执行 `upgrade head`；
  - 资源回收：`teardown()` 释放引擎；
  - orjson 集成：`models.base` 提供 `orjson_dumps/_compact`，用于高效 JSON 序列化。

- 统一时间与时区：
  - `models/base.py` 定义 `now_naive()` 与 `to_naive_beijing()`，均返回无时区的北京时间；
  - 各模型通过 `model_validator/field_validator` 在入模与赋值时将 ISO 字符串/UTC 转换为北京 naive 时间。

- 用户模型（user）：
  - 表：`users`，字段含 `username`（唯一索引）、`password_hash`、`role`、`is_active`、`member_id`（唯一外键）、时间戳与 `last_login`；
  - CRUD：按用户名/ID/成员ID查询，创建/更新/删除/统计，`update_last_login` 更新最后登录时间；
  - 数据规范：`ConfigDict(validate_assignment=True)`，时间字段在入模与赋值阶段强制归一化。

- 成员模型（member）：
  - 表：`members`，对外公开 `id`；核心字段：`display_name`、`group_nick`、`qq_nick`、`uin_encrypted`、`salt`、`role(0/1/2)`、`join_time`、`last_speak_time`、等级/年龄与时间戳；
  - CRUD：
    - 读优化：`get_by_id`/`get_many_by_ids` 首选全局缓存（`services/cache`），批量读支持 `get_many`/`set_many`；
    - 写后回写：`create/update/delete` 同步更新或删除缓存；
    - 分页/模糊/按角色/活跃度查询与统计；
  - 配置化 TTL：通过 `ConfigService.settings.cache_member_ttl` 控制成员缓存过期时间（默认 300s）。

- Alembic：
  - 版本历史置于 `src/backend/alembic/versions`，对应初始表、评论、活动、JSONB 字段等迁移；
  - 正式环境建议以迁移为准，`create_all` 作为本地开发兜底。

### API 路由集合（api/v1/*, api/router.py）

- 路由组装：`api/router.py` 将 v1 路由以 `/api/v1` 前缀汇总；注册顺序避免路径吞并（先 `users_bind` 再 `members`）。

- 认证（auth.py）：
  - `POST /auth/login`：OAuth2 表单鉴权，签发 JWT，更新 `last_login`；
  - `GET /auth/me`：返回当前用户信息（依赖 `get_current_active_user`）；
  - `POST /auth/logout`：无状态占位，前端清 token 即可；
  - `POST /auth/register`、`POST /auth/change-password`、`POST /auth/refresh` 完整用户周期。

- 成员（members.py）：
  - 列表/详情/统计：`GET /members`、`GET /members/{id}`、`GET /members/stats`；
  - 管理操作（需管理员）：`POST /members`、`PUT /members/{id}`、`DELETE /members/{id}`；
  - 导入：`POST /members/import`（JSON 批量 upsert）、`POST /members/import-file`、`POST /members/import-from-qq`；
  - 头像刷新：`POST /members/refresh-avatars`；
  - 说明：大量读操作结合全局缓存，写后同步回写/删除缓存。

- 其他模块：
  - 活动：`activities.py`（新系统接口，含排名/选项/投票）；
  - 配置：`configs.py`（CRUD 与分页）；
  - 评论：`comments.py`（成员评论域）；`daily.py` 与 `daily_comments.py`（日常帖子与评论域）；
  - 绑定/头像/缓存：`users_bind.py`、`avatars.py`、`cache.py`；
  - 初始化：`setup.py`（首启引导与工具端点）。

### 缓存服务（services/cache/*）

- 实现：
  - 基于 `cachetools.TTLCache` 封装为异步安全服务，辅以 `asyncio.Lock`；
  - 统计 `hits/misses/total_requests/hit_rate/cache_size/last_updated`；
  - 支持自定义 TTL：通过包装 `{ value, expire_time }` 实现 per-key TTL 行为；
  - 批量操作：`get_many`/`set_many`；装饰器：`cached(ttl, key_prefix)`。

- 配置：
  - 由 `CacheServiceFactory.create(config_service)` 读取 `settings.cache_max_size` 与 `settings.cache_default_ttl`；
  - 结合成员/统计等业务定义的专用 TTL：如 `cache_member_ttl`、`cache_stats_ttl`。

- 集成点：
  - Lifespan 启动时初始化并注入全局实例；
  - 成员 CRUD 读写路径结合缓存；统计接口结果按配置 TTL 缓存；
  - 提供管理端点（`api/v1/cache`）用于查看统计与清理键值。

### 加密服务（services/crypto/*）

- 设计：
  - 主密钥来源优先级：`UIN_AES_KEY` 环境变量 > `ConfigService.ensure_secret_key()` 文件；
  - 二次派生：通过 PBKDF2HMAC(SHA256) + 固定盐 `vd_member_salt_2024` 生成 32 字节 AES-256 密钥；
  - 算法：`AESGCM`（12 字节 nonce）；密文采用 `base64(nonce + cipher)` 便于存储。

- 能力：
  - `encrypt_uin(uin, salt)`：将 `uin` 与 `salt` 混合后加密；
  - `decrypt_uin(encrypted, salt)`：严格校验混合后缀 `vd{salt}`，失败抛显式错误；
  - 工具：头像命名 `generate_avatar_hash/secure_filename`，以 `uin+salt` 生成稳定哈希。

- 集成：
  - Lifespan 初始化时创建并注入；
  - 成员导入与头像批处理使用解密 UIN 与安全文件名；
  - 与配置服务耦合以获取/持久化密钥。

### Schema（src/backend/schema/*.py）

- 作用：对外 API 的请求/响应 Pydantic 模型，隔离内部 SQLModel；统一时间序列化为 ISO 字符串（必要时补 UTC）。

- 成员（member.py）：
  - 响应：`MemberResponse/MemberDetailResponse`、分页 `MemberListResponse`；
  - 导入：`ImportMemberRequest`、`ImportBatchRequest`；
  - 常用：`CreateMemberRequest`、通用 `ApiResponse/ErrorResponse`；
  - 绑定视图：`BindableMemberItem/BindableMembersResponse`。

- 活动（activity.py）：
  - `ActivityResponse` 使用 `ConfigDict.json_encoders` 规范 datetime 输出；
  - `ParticipantInfo`、`ActivityListResponse`、`ActivityStatsResponse`、`ActivityCreate/UpdateRequest`。

- 评论（comment.py）：
  - `CommentResponse`/`CommentListResponse`/`CommentStatsResponse`；
  - `CommentCreateRequest` 与操作结果 `CommentActionResponse`；
  - 管理辅助 `CommentModerationResponse` 和通用 `ErrorResponse`。

- Daily（daily.py 与 daily_comment.py）：
  - 帖子：`DailyPostItem`（含富文本 JSONB 与 images/tags/计数），`DailyPostListResponse`，上传 `UploadImagesResponse` 等；
  - 评论：`DailyCommentItem`、`DailyCommentListResponse`、`DailyCommentCreateRequest`、`DailyCommentActionResponse`；
  - 时间字段统一使用序列化器或 `json_encoders` 输出 ISO 字符串。

### 领域层（domain/member_service.py）

- 职责：围绕成员的业务编排，连接 CRUD、加解密、头像、活动/评论清理、DTO 转换。
- 能力：
  - 响应构造：`create_member_response/detail_response` 统一头像 URL、简介、日期格式；
  - 分页与详情：`get_members_paginated`/`get_member_by_id`；
  - 导入 Upsert：`import_member_from_json`、`upsert_members_from_json`（批量解密构建 UIN→Member 映射、创建/更新、返回统计）；
  - 退群对账：`reconcile_departures` 删除评论、移除活动参与、清理头像、删除成员，返回详细统计；
  - 统一 HTML 实体解码与北京时间处理。

### 工具模块（utils）

- 头像（utils/avatar.py）：
  - 下载：`fetch_and_save_avatar_webp(uin)` 使用 httpx 拉取 QQ 头像并转换为 WebP（原子替换，避免半写）；
  - 批量：`batch_fetch_and_save_avatars_webp` 返回成功/失败统计；
  - 查询/删除：按 `uin` 读取或删除 `avatar_root/{uin}.webp`；
  - 目录：启动时由 Config 的 `avatar_root` 决定，必要时创建。

- QQ 抓取（utils/qq_group/fetcher.py）：
  - 提供 `fetch_members(group_id, cookie, bkn, ...)`，分页 POST 官方接口聚合返回 `mems` 等；
  - 失败抛 `QQGroupFetcherError`，支持 `request_delay` 限速。

- 上传（utils/uploads.py）：
  - 将上传图片保存至 `static/pics/yyyy/mm`，文件名随机；
  - 返回 `(name, url, width, height)`，URL 统一走 `/api/v1/daily/pics/...` API 以适配生产静态挂载；
  - 基础 MIME/内容检测与尺寸读取，支持 jpg/png/webp/gif。