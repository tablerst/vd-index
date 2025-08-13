# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 语言偏好 / Language Preference
用户偏好使用中文进行交流。Please respond in Chinese.

## 工作规范 / Working Standards

### 工具使用 / Tool Usage
1. **反馈工具**: 完成每个步骤后始终使用 feedback 工具向用户提供反馈
2. **顺序思考**: 使用 sequentialthinking 工具将复杂任务分解为可管理的小步骤
3. **任务管理**: 必须使用 taskList 有效规划和组织任务
4. **文档参考**: 涉及第三方库时，通过 Context7 参考最新官方文档

### 注释规范 / Comment Standards
1. **代码注释**: 所有代码注释使用英文，清晰简洁，解释代码目的而非仅描述操作
2. **Markdown文档**: 在编写markdown时使用中文注释，代码部分使用英文
3. **避免无效注释**: 不添加显而易见、无价值的注释

### 故障排查 / Troubleshooting
1. **错误分析**: 根据错误信息，分析调用链和堆栈跟踪的相关上下文
2. **在线搜索**: 错误信息不明确时，在线搜索类似问题和解决方案
3. **系统化排查**: 从最可能的原因开始，逐步缩小问题范围

### 代码生成 / Code Generation
1. **遵循现有风格**: 使用现有代码的结构和风格作为指导
2. **功能性优先**: 确保代码功能完整并符合项目编码标准
3. **最佳实践**: 遵循语言和框架的最佳实践

### 测试说明 / Testing Guidelines
- **不要运行测试**: 项目复杂，需要专门的测试环境
- **只编写测试**: 基于需求和现有代码编写测试用例
- **测试覆盖**: 考虑边界情况和异常处理

## 项目架构 / Project Architecture

### 整体架构
- **前后端分离架构**：Windows环境开发
  - `src/backend`: FastAPI + SQLAlchemy + PostgreSQL (使用 uv 包管理)
  - `src/frontend`: Vue3 + TypeScript + Vite (使用 pnpm 包管理)
- **开发模式**：前后端独立服务运行
- **生产模式**：FastAPI 服务静态文件，通过 nginx 80端口访问（域名：tomo-loop.icu）
- **部署脚本**：独立的 dev/prod 脚本，可复用的 deps 安装脚本
- **日志管理**：日志文件放在项目根目录（避免 uvicorn 热重载问题）

## Essential Commands

### Development / 开发命令
```bash
# 同时启动前后端开发模式
./scripts/dev.sh      # Linux/Mac
scripts\dev.bat       # Windows

# 分别启动:
# 后端 (FastAPI)
cd src/backend && uv run python -m run

# 前端 (Vue/Vite) - 使用 pnpm
cd src/frontend && pnpm dev
```

### Build & Production / 构建与生产
```bash
# 构建前端生产版本
cd src/frontend && pnpm build

# 生产部署 (nginx - Linux)
./scripts/prod.sh   # 使用 deploy.sh 直接部署

# Windows 生产环境 (仅后端)
scripts\prod.bat
```

### Database Operations / 数据库操作
```bash
cd src/backend

# 运行数据库迁移
uv run python -m alembic upgrade head

# 创建新迁移 (必须在 src/backend 目录执行)
uv run python -m alembic revision --autogenerate -m "description"

# 回滚迁移
uv run python -m alembic downgrade -1

# 导入QQ群成员数据
uv run python scripts/import_group_json.py static/qq_group_members.json

# 创建超级用户
uv run python -m services.auth.utils create_super_user
```

### Testing / 测试
```bash
# 后端测试 (pytest)
cd src/backend
uv run pytest

# 前端测试 (Playwright 视觉验证)
cd src/frontend
pnpm test  # 如果配置了测试

# 使用 Playwright 进行实时视觉验证
npx playwright test
```

### Linting & Type Checking / 代码检查
```bash
# 前端类型检查
cd src/frontend
pnpm build  # 包含 vue-tsc 类型检查

# 后端代码格式化和检查
cd src/backend
uv run black .
uv run pylint .
```

## 详细架构说明 / Detailed Architecture

### 系统设计 / System Design
**VD群成员管理系统** - 具有沉浸式3D视觉效果的全栈应用：

```
┌─────────────────────────────────────────────────┐
│           前端 Frontend (Vue 3 + TS)             │
│  技术栈：                                        │
│  - Vue 3 Composition API + TypeScript          │
│  - NaiveUI 组件库 + Pinia 状态管理              │
│  - Three.js 3D效果 + GSAP 动画                  │
│  - Swiper 分页 + SCSS 样式系统                  │
│  功能模块：                                      │
│  - 星际门效果 (2D/3D Ring)                      │
│  - 成员星云 (40-50人/页横向分页)                │
│  - 动态连接线 (呼吸效果+主题色混合)             │
│  - 全局粒子系统 (Teleport + Web Workers)       │
│  - 响应式主题系统 (6层架构)                     │
└─────────────────┬───────────────────────────────┘
                  │ /api/v1/* RESTful API
┌─────────────────▼───────────────────────────────┐
│           后端 Backend (FastAPI)                 │
│  核心功能：                                      │
│  - UIN加密 (AES-256-GCM + 独立salt)            │
│  - 代理ID系统 (永不暴露真实UIN)                 │
│  - 异步PostgreSQL (asyncpg + 连接池)           │
│  - 全局字典缓存 (MemberCache + 异步锁)         │
│  - JWT认证 (除首页/登录外全部保护)              │
│  数据流：                                        │
│  - CRUD先查缓存 → 数据库 → 更新缓存             │
│  - 批量操作同步缓存                             │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│         PostgreSQL 数据库                        │
│  - members: 加密UIN + 代理ID                    │
│  - activities: JSON成员列表 + 冗余总数          │
│  - config: 系统配置                             │
│  - comments: 评论系统                           │
│  - users: 管理员账户                            │
└─────────────────────────────────────────────────┘
```

## 开发规范 / Development Standards

### 后端开发规范 / Backend Standards
- **API版本控制**: 所有端点统一使用 `/api/v1` 前缀
- **路由管理**: 使用 `router.py` 集中管理路由
- **数据库模型组织**:
  ```
  services/database/models/
  ├── member/
  │   ├── base.py    # 模型定义
  │   └── crud.py    # CRUD操作
  ├── activity/
  ├── config/
  └── comment/
  ```
- **异步数据库**: 使用 asyncpg + 依赖注入 (services/deps.py)
- **数据库迁移**: 必须在 src/backend 目录执行 `python -m alembic`
- **缓存策略**: MemberCache 全局字典缓存，异步安全读写锁
- **安全设计**: UIN加密在后端处理，前端永不接触真实UIN

### 前端开发规范 / Frontend Standards
- **技术栈**: Vue3 + TypeScript + Vite + pnpm
- **UI框架**: NaiveUI (使用官方文档保持一致性)
- **目录结构**:
  ```
  src/frontend/src/
  ├── components/   # 组件 (HeroSection, MembersCircle, GalaxySlide)
  ├── views/        # 页面 (Home, Login, Settings/*)
  ├── stores/       # Pinia状态 (auth, members, theme)
  ├── services/     # API服务
  ├── composables/  # 组合式函数
  ├── utils/        # 工具函数
  └── styles/       # SCSS模块化样式
  ```
- **主题系统**: 6层架构 (Pinia→Provider→Config→UI→色彩科学→CSS变量)
- **测试验证**: 使用 Playwright 进行视觉验证
- **性能优化**: Canvas需要devicePixelRatio缩放，使用Web Workers

## 核心功能模块 / Core Features

### 视觉效果系统 / Visual Effects
- **星际门 (Stargate)**:
  - 2D实现: SVG三层同心圆 (#AA83FF/#D4DEC7/#3F7DFB)
  - CSS滤镜光晕 + GSAP呼吸动画
  - 鼠标视差交互 (2.5D效果)
  - 位置: 左侧480-520px，右侧文字内容

- **成员星云 (Member Galaxy)**:
  - 横向全屏分页，40-50人/页 (Swiper + GSAP)
  - 随机散布布局 (避免等级感)
  - 动态连接线系统:
    - 呼吸alpha效果 (0→1→0 使用sin(t·π))
    - 曲线连接，裁剪到头像圆边缘
    - 3-5秒随机激活2-4条线，持续4-5秒
    - 主题色混合渐变，高亮度显示

- **粒子系统 (Particles)**:
  - 全局粒子: Teleport突破容器限制
  - 中心密度增强，特定梯度递减
  - 环形粒子: OffscreenCanvas + Web Workers
  - 性能自适应 (45fps阈值监控)

### 路由设计 / Route Design
- `/` - 主页 (成员星云展示)
- `/badge-preview` - 3D徽章预览
- `/login` - 管理员登录
- `/settings` - 后台管理
  - `/settings/dashboard` - 仪表板
  - `/settings/members` - 成员管理
  - `/settings/activities` - 活动管理
  - `/settings/config` - 配置管理

## API接口 / API Endpoints

### 公开接口 (无需认证)
```
GET  /api/v1/members?page={n}&page_size={m}  # 成员列表
GET  /api/v1/members/{id}                    # 成员详情
GET  /api/avatar/{member_id}                 # 头像图片
GET  /api/v1/star_calendar/activities        # 活动列表
GET  /api/v1/comments/members/{id}/comments  # 评论列表
POST /api/v1/auth/login                      # 登录
POST /api/v1/auth/logout                     # 登出
```

### 管理接口 (需要JWT认证)
```
POST /api/v1/members/import                  # 导入JSON
POST /api/v1/members/import-from-qq          # QQ群导入
POST /api/v1/members/create                  # 创建成员
PUT  /api/v1/members/{id}                    # 更新成员
DELETE /api/v1/members/{id}                  # 删除成员
GET  /api/v1/cache/stats                     # 缓存统计
POST /api/v1/cache/clear                     # 清空缓存
```

## 环境配置 / Environment Configuration

### 后端配置 (.env)
```bash
# 数据库 (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/vd_index

# 文件存储
AVATAR_ROOT=./data/avatars

# 加密密钥 (可选，默认使用 secret_key 文件)
# UIN_AES_KEY=<32-char-key>

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false  # 生产环境必须为false

# CORS配置 (生产环境)
ALLOWED_ORIGINS=["https://tomo-loop.icu"]
ALLOWED_HOSTS=["tomo-loop.icu"]

# 缓存配置
CACHE_MAX_SIZE=10000
CACHE_DEFAULT_TTL=300
CACHE_MEMBER_TTL=300

# 超级用户
SUPER_USER_USERNAME=admin
SUPER_USER_PASSWORD=change-this-in-production
```

### 前端配置
- **开发环境**: Vite代理 `/api` 到 `http://localhost:8000`
- **生产环境**: 相对路径，由FastAPI服务静态文件
- **域名访问**: tomo-loop.icu (nginx 80端口)

## UI设计偏好 / UI Design Preferences

### 布局设计
- **星际门**: 左侧定位 (480-520px)，右侧文字内容
- **成员布局**: 随机散布 (避免等级感)，围绕中央分页框
- **横向分页**: 全屏40-50人/页，左右箭头导航 (Swiper)
- **管理界面**: 统一深色主题，非透明模态框

### 连接线设计
- **动态效果**: 真实呼吸效果 (弱→强→弱渐变)
- **视觉样式**: 主题色混合渐变，高亮度显示
- **激活机制**: 3-5秒随机激活2-4条线，持续4-5秒
- **路径设计**: 二次曲线，裁剪到头像边缘
- **时间轴连接**: 节点延伸短线到评论框，无箭头设计

### 颜色设计
- **管理员徽章**: 浅绿色
- **主题一致性**: 所有界面统一主题色
- **文字颜色**: 使用 var(--text-primary/secondary/inverse)
- **n-tag/n-transfer**: 深色主题色代替白色

## 性能优化 / Performance Optimization

### Canvas渲染
```javascript
// HiDPI屏幕优化
const dpr = window.devicePixelRatio || 1
canvas.width = rect.width * dpr
canvas.height = rect.height * dpr
ctx.scale(dpr, dpr)
```

### 移动端优化 (useSnapScroll)
- **设备检测**: mobile/tablet/desktop智能识别
- **差异化配置**: 
  - 移动端: 0.8s动画, 30px阈值, 速度检测
  - 桌面端: 1.2s动画, 50px阈值
- **手势识别**: 距离+速度+方向综合判断
- **性能提升**: 50%响应速度, 67%准确率

### 数据库优化
- 连接池: size=10, max_overflow=20
- 全局缓存: MemberCache + 异步安全锁
- CRUD优化: 先查缓存→数据库→更新缓存

### 前端分包
```javascript
manualChunks: {
  'vendor-vue': ['vue', 'pinia'],
  'vendor-three': ['three'],
  'vendor-gsap': ['gsap'],
  'vendor-swiper': ['swiper']
}
```

## 常见问题 / Common Issues

1. **粒子卡顿**: 检查 useDeviceDetection 配置，减少粒子数量
2. **数据库连接失败**: 确认PostgreSQL运行，检查DATABASE_URL
3. **头像404**: 确认文件在 AVATAR_ROOT，检查成员是否存在
4. **CORS错误**: 更新后端.env中的ALLOWED_ORIGINS
5. **构建失败**: 前端运行 `pnpm install`，后端运行 `uv sync`
6. **热重载问题**: 日志文件移到项目根目录避免触发
7. **连接线不显示**: 检查初始激活设置，避免空白屏幕
8. **主题色不一致**: 确保使用CSS变量而非硬编码颜色

## 重要提醒 / Important Notes

- **安全性**: UIN加密必须在后端处理，前端永不接触真实UIN
- **认证保护**: 除首页和登录外，所有API需要JWT认证
- **视觉验证**: 使用Playwright进行实时视觉效果验证
- **文档参考**: 使用Context7获取最新官方文档
- **部署方式**: 生产环境使用deploy.sh直接部署
- **SQLite遗留代码**: 数据库已迁移到PostgreSQL，需清理旧代码