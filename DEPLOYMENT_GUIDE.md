# VRC Division 项目部署指南

## 项目概述

VRC Division 是一个前后端分离的 Vue.js + FastAPI 项目，支持开发模式和生产模式两种部署方式。

### 架构说明

- **前端**: Vue 3 + TypeScript + Vite + Three.js
- **后端**: FastAPI + SQLModel + PostgreSQL + AsyncPG
- **包管理**: 前端使用 npm，后端使用 uv
- **部署模式**:
  - **开发模式**: 前后端分别运行，支持热重载
  - **生产模式**: 前端构建为静态文件，由 FastAPI 统一提供服务

## 环境要求

### 系统要求
- **操作系统**: Windows 10+ / Ubuntu 18+ / macOS 10.15+
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 13+

### 必需工具
```bash
# Python 包管理器
pip install uv

# Node.js 包管理器 (通常随 Node.js 安装)
npm --version
```

## 数据准备

### 1. QQ群成员数据文件

**文件位置**: `src/backend/static/qq_group_937303337_members.json`

**获取方式**:
1. 使用 QQ 群管理工具导出群成员信息
2. 确保 JSON 格式包含以下字段：
```json
{
  "mems": [
    {
      "uin": 123456789,
      "card": "群昵称",
      "nick": "QQ昵称", 
      "role": 2,
      "join_time": 1640995200,
      "last_speak_time": 1640995200,
      "lv": {
        "point": 100,
        "level": 1
      },
      "qage": 365
    }
  ]
}
```

**字段说明**:
- `uin`: QQ号码
- `card`: 群昵称
- `nick`: QQ昵称
- `role`: 角色 (0=群主, 1=管理员, 2=群员)
- `join_time`: 加群时间 (Unix时间戳)
- `last_speak_time`: 最后发言时间
- `lv.point`: 等级积分
- `lv.level`: 等级
- `qage`: Q龄 (天数)

### 2. 成员头像文件

**文件位置**: `src/backend/static/avatars/mems/`

**文件命名**: `{uin}.webp` (例如: `123456789.webp`)

**获取方式**:
1. 使用 QQ 头像 API: `https://q1.qlogo.cn/g?b=qq&nk={uin}&s=640`
2. 批量下载并转换为 webp 格式
3. 确保文件名与 QQ 号码一致

**示例脚本** (可选):
```bash
# 批量下载头像 (需要自行实现)
# 将下载的头像文件放置到指定目录
```

## 环境配置

### 1. 后端环境配置

复制并配置环境文件：
```bash
cd src/backend
cp .env.example .env
```

**编辑 `.env` 文件**:
```env
# 数据库配置 (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/vd_index

# 头像文件存储路径
AVATAR_ROOT=./static/avatars/mems

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true  # 开发模式设为 true，生产模式设为 false

# CORS配置
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:5175","http://localhost:3000"]
ALLOWED_HOSTS=["localhost","127.0.0.1"]

# 速率限制
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### 2. 数据库配置

**创建数据库**:
```sql
-- 连接到 PostgreSQL
CREATE DATABASE vd_index;
CREATE USER vd_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE vd_index TO vd_user;
```

**更新 .env 中的数据库连接**:
```env
DATABASE_URL=postgresql+asyncpg://vd_user:your_password@localhost:5432/vd_index
```

### 3. 前端环境配置

前端环境变量已预配置：
- **开发环境**: `src/frontend/.env.development`
- **生产环境**: `src/frontend/.env.production`

通常无需修改，除非更改了后端端口。

## 部署前检查

在开始部署之前，建议运行环境检查脚本来验证系统配置：

```bash
# Windows
scripts\check-environment.bat

# Linux/macOS
chmod +x scripts/check-environment.sh
./scripts/check-environment.sh
```

**检查内容包括**:
- 系统工具 (Python, Node.js, npm, uv, PostgreSQL)
- 项目文件结构
- 数据文件 (QQ群成员JSON、头像文件)
- 环境配置 (.env 文件)

根据检查结果修复任何 ❌ FAIL 项目后再继续部署。

## 部署步骤

### 方式一：使用部署脚本 (推荐)

#### 1. 安装依赖
```bash
# Windows
scripts\install-deps.bat

# Linux/macOS  
chmod +x scripts/install-deps.sh
./scripts/install-deps.sh
```

#### 2. 开发模式部署
```bash
# Windows
scripts\dev.bat

# Linux/macOS
chmod +x scripts/dev.sh
./scripts/dev.sh
```

**开发模式特点**:
- 前端运行在 `http://localhost:5173`
- 后端运行在 `http://localhost:8000`
- 支持热重载和实时调试
- 前后端分别启动，便于开发

#### 3. 生产模式部署

**Linux/macOS (推荐，包含 nginx)**:
```bash
chmod +x scripts/prod.sh
./scripts/prod.sh
```

**Windows (仅后端)**:
```bash
scripts\prod.bat
```

**生产模式特点**:
- 前端构建为静态文件
- 后端运行在 http://localhost:8000
- Nginx 提供域名访问 (Linux/macOS)
- 优化的构建输出和缓存设置
- 自动启动和进程管理

**生产部署完成后**:
- **域名访问**: http://tomo-loop.icu (通过 nginx)
- **直接访问**: http://localhost:8000 (直接访问后端)
- **API 文档**: http://localhost:8000/docs

**管理生产服务**:
```bash
# 查看 nginx 状态
./scripts/nginx-control.sh status

# 重启 nginx
./scripts/nginx-control.sh restart

# 查看后端日志
tail -f logs/backend.log

# 查看 nginx 日志
./scripts/nginx-control.sh logs
```

### 方式二：手动部署

#### 1. 安装依赖
```bash
# 安装前端依赖
cd src/frontend
npm install

# 安装后端依赖
cd ../backend
uv sync
```

#### 2. 数据导入
```bash
# 导入 QQ 群成员数据
cd src/backend
python scripts/import_group_json.py static/qq_group_937303337_members.json
```

#### 3. 启动服务

**开发模式**:
```bash
# 启动后端 (终端1)
cd src/backend
uv run python -m run

# 启动前端 (终端2)
cd src/frontend  
npm run dev
```

**生产模式**:
```bash
# 构建前端
cd src/frontend
npm run build

# 复制静态文件
cp -r dist/* ../backend/static/

# 启动生产服务
cd ../backend
uv run python -m run
```

## 数据导入

### 导入群成员数据
```bash
cd src/backend

# 导入数据
python scripts/import_group_json.py static/qq_group_937303337_members.json

# 验证导入
python scripts/verify_import.py
```

### 验证头像文件
确保头像文件正确放置：
```bash
ls src/backend/static/avatars/mems/
# 应该看到类似 123456789.webp 的文件
```

## 访问应用

### 开发模式
- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 生产模式  
- **应用**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 文件结构说明

```
vd-index/
├── scripts/                    # 部署脚本
│   ├── check-environment.bat/.sh  # 环境检查脚本
│   ├── install-deps.bat/.sh   # 依赖安装
│   ├── dev.bat/.sh           # 开发模式启动
│   ├── prod.bat/.sh          # 生产模式部署
│   └── nginx-control.sh      # Nginx 管理脚本
├── src/
│   ├── frontend/             # 前端代码
│   │   ├── src/             # Vue 源码
│   │   ├── package.json     # 前端依赖
│   │   ├── .env.development # 开发环境配置
│   │   └── .env.production  # 生产环境配置
│   └── backend/             # 后端代码
│       ├── static/          # 静态文件目录
│       │   ├── avatars/     # 头像文件
│       │   │   └── mems/    # 成员头像 (*.webp)
│       │   └── qq_group_937303337_members.json  # 群成员数据
│       ├── scripts/         # 数据导入脚本
│       ├── .env            # 后端环境配置
│       ├── .env.example    # 环境配置示例
│       ├── pyproject.toml  # Python 依赖
│       └── run.py          # 启动脚本
└── DEPLOYMENT_GUIDE.md     # 本部署指南
```

## 常见问题

### 1. 数据库连接失败
**问题**: `asyncpg.exceptions.InvalidCatalogNameError`
**解决**: 确保数据库已创建且连接信息正确

### 2. 头像显示 404
**问题**: 成员头像无法显示
**解决**: 
- 检查头像文件是否存在于 `src/backend/static/avatars/mems/`
- 确认文件命名格式为 `{uin}.webp`
- 检查 `.env` 中 `AVATAR_ROOT` 配置

### 3. CORS 错误
**问题**: 前端无法访问后端 API
**解决**: 检查 `.env` 中 `ALLOWED_ORIGINS` 配置

### 4. 端口占用
**问题**: 端口 5173 或 8000 被占用
**解决**: 
- 修改 `.env` 中的 `PORT` 配置
- 或终止占用端口的进程

### 5. uv 命令不存在
**问题**: `uv: command not found`
**解决**: 
```bash
pip install uv
# 或使用 python -m pip install uv
```

## 生产环境建议

### 安全配置
1. 使用强密码和密钥
2. 限制 CORS 到实际域名
3. 配置防火墙和反向代理
4. 定期备份数据库

### 性能优化
1. 使用 CDN 加速静态资源
2. 配置数据库连接池
3. 启用 gzip 压缩
4. 监控系统资源使用

### 监控和日志
1. 配置应用日志
2. 监控数据库性能
3. 设置错误告警
4. 定期检查系统状态

## 高级配置

### 1. 生产环境 .env 配置示例

```env
# 生产环境配置
DATABASE_URL=postgresql+asyncpg://vd_user:strong_password@localhost:5432/vd_index
AVATAR_ROOT=./static/avatars/mems
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 生产域名配置
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com","www.yourdomain.com"]

# 增强安全配置
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=60
```

### 2. Nginx 配置 (生产环境推荐)

项目已包含预配置的 nginx 配置文件 `nginx.conf`，配置了：
- 域名: `tomo-loop.icu`
- 静态文件服务
- API 代理到后端
- 头像文件缓存
- 安全头设置

**使用 nginx 控制脚本**:
```bash
# 启动 nginx
./scripts/nginx-control.sh start

# 停止 nginx
./scripts/nginx-control.sh stop

# 重启 nginx
./scripts/nginx-control.sh restart

# 查看状态
./scripts/nginx-control.sh status

# 测试配置
./scripts/nginx-control.sh test

# 查看日志
./scripts/nginx-control.sh logs
```

**手动 nginx 配置** (如需自定义):
```nginx
server {
    listen 80;
    server_name tomo-loop.icu;

    root /path/to/vd-index/src/backend/static;
    index index.html;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /avatars/ {
        proxy_pass http://localhost:8000;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 3. 系统服务配置 (Linux)

创建 systemd 服务文件 `/etc/systemd/system/vd-index.service`:

```ini
[Unit]
Description=VRC Division Index Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/vd-index/src/backend
Environment=PATH=/path/to/vd-index/.venv/bin
ExecStart=/path/to/vd-index/.venv/bin/python -m run
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable vd-index
sudo systemctl start vd-index
sudo systemctl status vd-index
```

## 故障排除

### 数据库相关问题

**问题**: 数据库连接超时
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 检查数据库连接
psql -h localhost -U vd_user -d vd_index -c "SELECT 1;"
```

**问题**: 数据导入失败
```bash
# 检查 JSON 文件格式
python -m json.tool static/qq_group_937303337_members.json

# 手动验证数据库连接
cd src/backend
python -c "from core.config import get_settings; print(get_settings().database_url)"
```

### 权限相关问题

**问题**: 头像文件访问权限
```bash
# 设置正确的文件权限
chmod -R 644 src/backend/static/avatars/mems/
chmod 755 src/backend/static/avatars/mems/
```

**问题**: 静态文件目录权限
```bash
# 确保 Web 服务器可以访问静态文件
chown -R www-data:www-data src/backend/static/
```

### 网络相关问题

**问题**: API 请求失败
```bash
# 测试后端 API
curl http://localhost:8000/health
curl http://localhost:8000/api/members

# 检查防火墙设置
sudo ufw status
sudo ufw allow 8000
```

### 性能问题

**问题**: 应用响应慢
```bash
# 监控系统资源
htop
iostat -x 1

# 检查数据库性能
psql -U vd_user -d vd_index -c "SELECT * FROM pg_stat_activity;"
```

## 备份和恢复

### 数据库备份
```bash
# 创建备份
pg_dump -U vd_user -h localhost vd_index > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
psql -U vd_user -h localhost vd_index < backup_20240101_120000.sql
```

### 完整项目备份
```bash
# 备份整个项目 (排除 node_modules 和 .git)
tar --exclude='node_modules' --exclude='.git' --exclude='__pycache__' \
    -czf vd-index-backup-$(date +%Y%m%d).tar.gz vd-index/
```

## 更新和维护

### 更新依赖
```bash
# 更新前端依赖
cd src/frontend
npm update

# 更新后端依赖
cd ../backend
uv sync --upgrade
```

### 数据库迁移
```bash
# 如果数据库结构有变化
cd src/backend
python -c "
from services.database.utils import run_migrations
import asyncio
asyncio.run(run_migrations())
"
```

### 日志管理
```bash
# 查看应用日志 (如果使用 systemd)
sudo journalctl -u vd-index -f

# 清理旧日志
sudo journalctl --vacuum-time=30d
```

## 监控建议

### 健康检查
```bash
# 定期检查应用状态
curl -f http://localhost:8000/health || echo "Service is down"

# 检查数据库连接
curl -f http://localhost:8000/api/members?page=1&page_size=1 || echo "Database issue"
```

### 自动化监控脚本
```bash
#!/bin/bash
# monitor.sh - 简单的监控脚本

check_service() {
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "$(date): Service OK"
    else
        echo "$(date): Service DOWN - Restarting..."
        sudo systemctl restart vd-index
    fi
}

# 每5分钟检查一次
while true; do
    check_service
    sleep 300
done
```

---

**部署完成后，访问应用验证所有功能正常工作！**

如有问题，请检查日志文件或参考故障排除部分。
