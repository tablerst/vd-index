# Nginx 启动问题解决方案

## 问题描述
在Ubuntu服务器上运行 `prod.sh` 时出现错误：
```
nginx: [emerg] open() "/usr/share/nginx/./logs/error.log" failed (2: No such file or directory)
Error: Failed to start nginx
```

## 问题原因
1. **相对路径问题**：nginx.conf 中使用了相对路径 `./logs/error.log`
2. **工作目录不匹配**：nginx 启动时的工作目录不是项目根目录
3. **路径解析错误**：nginx 将相对路径解析为 `/usr/share/nginx/./logs/error.log`

## 解决方案

### 方案1：使用动态配置生成脚本（推荐）
已创建 `scripts/generate-nginx-conf.sh` 脚本，会根据实际项目路径动态生成正确的nginx配置。

**使用方法：**
```bash
# 在项目根目录下
chmod +x scripts/generate-nginx-conf.sh
./scripts/generate-nginx-conf.sh tomo-loop.icu /path/to/your/project
```

**自动集成：**
- `prod.sh` 脚本已更新，会自动调用配置生成脚本
- `nginx-control.sh` 脚本也已更新

### 方案2：手动修复现有配置
如果你想手动修复，需要将 nginx.conf 中的相对路径改为绝对路径：

```nginx
# 修改前
error_log ./logs/error.log;
pid ./logs/nginx.pid;
access_log ./logs/access.log main;

# 修改后（替换为你的实际项目路径）
error_log /path/to/your/project/logs/error.log;
pid /path/to/your/project/logs/nginx.pid;
access_log /path/to/your/project/logs/access.log main;
```

## 部署步骤

### 在Ubuntu服务器上：

1. **确保项目路径正确**
   ```bash
   cd /path/to/your/project
   pwd  # 确认当前路径
   ```

2. **给脚本添加执行权限**
   ```bash
   chmod +x scripts/*.sh
   ```

3. **运行生产部署**
   ```bash
   ./scripts/prod.sh
   ```

4. **或者单独管理nginx**
   ```bash
   # 启动
   ./scripts/nginx-control.sh start
   
   # 停止
   ./scripts/nginx-control.sh stop
   
   # 重启
   ./scripts/nginx-control.sh restart
   
   # 查看状态
   ./scripts/nginx-control.sh status
   ```

## 验证步骤

1. **检查配置文件生成**
   ```bash
   cat nginx.conf | grep error_log
   cat nginx.conf | grep access_log
   ```

2. **测试nginx配置**
   ```bash
   sudo nginx -t -c /path/to/your/project/nginx.conf
   ```

3. **检查日志目录**
   ```bash
   ls -la logs/
   ```

4. **验证服务运行**
   ```bash
   curl -I http://tomo-loop.icu
   ```

## 常见问题

### Q: 权限问题
如果遇到权限问题，确保：
- nginx 以 root 用户运行（配置中已设置）
- 项目目录对 root 用户可读
- 日志目录存在且可写

### Q: 端口占用
如果80端口被占用：
```bash
sudo netstat -tlnp | grep :80
sudo systemctl stop nginx  # 停止系统nginx服务
```

### Q: 域名解析
确保域名 `tomo-loop.icu` 正确解析到服务器IP：
```bash
nslookup tomo-loop.icu
```

## 文件结构
```
project/
├── nginx.conf                    # 动态生成的nginx配置
├── logs/                         # nginx日志目录
│   ├── access.log
│   ├── error.log
│   └── nginx.pid
├── scripts/
│   ├── generate-nginx-conf.sh    # 配置生成脚本
│   ├── nginx-control.sh          # nginx控制脚本
│   └── prod.sh                   # 生产部署脚本
└── src/
    └── backend/
        └── static/               # 前端构建文件
```
