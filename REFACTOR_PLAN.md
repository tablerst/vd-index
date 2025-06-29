# 前后端分离重构计划

## 项目概述

将当前项目重构为前后端分离架构，支持开发模式和生产模式的不同部署方式。

## 目标架构

### 开发模式 (dev)
- 前端：独立运行在 `localhost:5173` (Vite dev server)
- 后端：独立运行在配置的端口 (FastAPI + uvicorn)
- 前后端通过 API 接口通信

### 生产模式 (prod)
- 前端：构建为静态文件，由 FastAPI 作为静态文件服务
- 后端：FastAPI 同时提供 API 服务和静态文件服务
- 单一服务端口对外提供服务

## 脚本设计

### 1. deps 脚本 (install-deps.bat/install-deps.sh)
**功能：** 安装前后端所有依赖
```bash
# 前端依赖安装
cd src/frontend
npm install

# 后端依赖安装  
cd ../backend
uv sync
```

### 2. dev 脚本 (dev.bat/dev.sh)
**功能：** 启动开发环境（前后端分别启动）
```bash
# 启动后端服务（后台运行）
cd src/backend
start python3 -m run

# 启动前端服务
cd ../frontend  
npm run dev
```

### 3. prod 脚本 (prod.bat/prod.sh)
**功能：** 构建并启动生产环境
```bash
# 安装依赖（复用 deps 脚本）
call install-deps.bat

# 构建前端
cd src/frontend
npm run build

# 将构建文件移动到后端静态目录
xcopy /E /I /Y dist\* ..\backend\static\

# 启动生产服务
cd ../backend
python3 -m run
```

## 实现步骤

### 阶段 1：脚本创建
- [x] 创建 `scripts/install-deps.bat` 和 `scripts/install-deps.sh`
- [x] 创建 `scripts/dev.bat` 和 `scripts/dev.sh`  
- [x] 创建 `scripts/prod.bat` 和 `scripts/prod.sh`

### 阶段 2：前端适配
- [ ] 修改前端构建配置，确保生产构建输出到 `dist` 目录
- [ ] 配置前端 API 基础路径，支持开发和生产环境
- [ ] 更新前端环境变量配置
- [ ] 测试前端独立运行

### 阶段 3：后端适配  
- [ ] 配置 FastAPI 静态文件服务
- [ ] 更新后端 CORS 配置，支持开发模式跨域
- [ ] 确保后端 API 路径与前端配置匹配
- [ ] 测试后端独立运行

### 阶段 4：集成测试
- [ ] 测试开发模式：前后端分离运行
- [ ] 测试生产模式：FastAPI 服务静态文件
- [ ] 验证 API 通信正常
- [ ] 性能和功能测试

## 技术要点

### 前端配置
- **Vite 配置：** 支持不同环境的 API 代理和构建输出
- **环境变量：** 区分开发和生产环境的 API 基础路径
- **构建优化：** 确保生产构建文件适合静态服务

### 后端配置
- **静态文件服务：** FastAPI mount 静态文件目录
- **CORS 配置：** 开发模式允许跨域，生产模式限制域名
- **路由设计：** API 路径与静态文件路径不冲突

### 部署考虑
- **依赖管理：** 前端使用 npm，后端使用 uv
- **构建流程：** 自动化构建和文件移动
- **环境隔离：** 开发和生产环境配置分离

## 文件结构

```
vd-index/
├── scripts/
│   ├── install-deps.bat
│   ├── install-deps.sh  
│   ├── dev.bat
│   ├── dev.sh
│   ├── prod.bat
│   └── prod.sh
├── src/
│   ├── frontend/
│   │   ├── src/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── .env.development/.env.production
│   └── backend/
│       ├── app/
│       ├── static/          # 生产模式静态文件目录
│       ├── pyproject.toml
│       └── run.py
└── REFACTOR_PLAN.md
```

## 验收标准

1. **deps 脚本**：能够正确安装前后端所有依赖
2. **dev 脚本**：能够同时启动前后端服务，支持热重载
3. **prod 脚本**：能够构建前端并启动生产服务
4. **功能完整性**：所有现有功能在新架构下正常工作
5. **性能要求**：生产模式性能不低于当前实现
