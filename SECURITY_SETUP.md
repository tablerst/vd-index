# 安全配置指南

本项目已清理所有敏感信息，请按照以下步骤配置您的环境。

## 1. 后端环境配置

### 创建环境变量文件
复制示例文件并根据您的环境修改：

```bash
cp src/backend/.env.example src/backend/.env
```

### 编辑 .env 文件
根据您的实际情况修改以下配置：

```env
# 生产环境设置
DEBUG=false
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./data/members.db

# 头像文件存储
AVATAR_ROOT=./data/avatars

# CORS配置（替换为您的实际域名）
ALLOWED_ORIGINS=["https://your-domain.com"]
ALLOWED_HOSTS=["localhost","127.0.0.1","your-domain.com"]

# 速率限制
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## 2. QQ群成员数据

### 准备成员数据文件
1. 将您的QQ群成员数据文件重命名为：`qq_group_XXXXXX_members.json`
2. 放置在：`src/backend/static/` 目录下
3. 参考示例文件：`src/backend/static/qq_group_members.example.json`

### 头像文件
1. 将成员头像文件放置在：`src/backend/data/avatars/` 目录下
2. 文件命名格式：`{avatar_hash}.webp`
3. 或者放置在：`src/backend/static/avatars/mems/` 目录下
4. 文件命名格式：`{uin}.webp`

## 3. Nginx 配置

### 修改域名
编辑 `nginx.conf` 文件，将 `your-domain.com` 替换为您的实际域名：

```nginx
server_name your-actual-domain.com www.your-actual-domain.com;
```

## 4. 密钥文件

系统会在首次运行时自动生成 `src/backend/secret_key` 文件。
如需手动创建，请确保文件权限设置为 600（仅所有者可读写）。

## 5. 数据库初始化

运行初始化脚本：

```bash
cd src/backend
python3 scripts/init_database.py
```

## 6. 安全注意事项

1. **永远不要提交敏感文件到版本控制系统**
2. **定期更换密钥和密码**
3. **限制文件访问权限**
4. **使用HTTPS进行生产部署**
5. **定期备份数据库文件**

## 7. 文件权限设置

```bash
# 设置密钥文件权限
chmod 600 src/backend/secret_key

# 设置数据目录权限
chmod 755 src/backend/data
chmod 644 src/backend/data/members.db

# 设置头像目录权限
chmod 755 src/backend/data/avatars
chmod 644 src/backend/data/avatars/*
```

## 8. 环境变量说明

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| DEBUG | 调试模式 | false |
| HOST | 服务器地址 | 0.0.0.0 |
| PORT | 服务器端口 | 8000 |
| DATABASE_URL | 数据库连接 | sqlite:///./data/members.db |
| AVATAR_ROOT | 头像存储路径 | ./data/avatars |
| ALLOWED_ORIGINS | 允许的跨域源 | ["https://your-domain.com"] |
| ALLOWED_HOSTS | 允许的主机 | ["localhost","your-domain.com"] |

请确保在部署前完成所有配置步骤。
