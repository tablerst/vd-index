# 头像功能调试指南

## 问题描述
本地环境可以正常获取头像，但远程环境出现 "UIN解密失败" 错误。

## 调试工具说明

### 1. 快速测试脚本 (`quick_avatar_test.py`)
**用途**: 快速检查基本功能是否正常
**使用方法**:
```bash
cd src/backend
python3 scripts/quick_avatar_test.py
```

**检查项目**:
- 密钥获取
- 头像目录存在性
- 数据库连接
- 单个成员的UIN解密

### 2. 详细调试脚本 (`debug_avatar.py`)
**用途**: 详细诊断各个组件的状态
**使用方法**:
```bash
cd src/backend
python3 scripts/debug_avatar.py
```

**检查项目**:
- 环境信息（工作目录、配置等）
- 加密功能（密钥生成、加密解密测试）
- 数据库连接和成员数据

### 3. 环境对比脚本 (`env_compare.py`)
**用途**: 对比本地和远程环境的差异
**使用方法**:
```bash
# 在本地环境运行
cd src/backend
python3 scripts/env_compare.py > local_env.txt

# 在远程环境运行
cd src/backend
python3 scripts/env_compare.py > remote_env.txt

# 对比两个文件
diff local_env.txt remote_env.txt
```

## 调试步骤

### 第一步：快速检查
1. 在本地环境运行 `quick_avatar_test.py`，确认本地环境正常
2. 在远程环境运行 `quick_avatar_test.py`，查看哪一步失败

### 第二步：详细诊断
如果快速测试发现问题，运行 `debug_avatar.py` 获取详细信息：
```bash
cd src/backend
python3 scripts/debug_avatar.py 2>&1 | tee debug_output.log
```

### 第三步：环境对比
运行环境对比脚本，找出本地和远程环境的差异：
```bash
python3 scripts/env_compare.py
```

### 第四步：查看应用日志
启动应用后，查看详细日志：
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 常见问题和解决方案

### 1. 密钥不一致
**症状**: "UIN解密失败" 错误
**检查**:
- 环境变量 `UIN_AES_KEY` 是否设置
- `secret_key` 文件是否存在且内容一致
- 密钥文件的哈希值是否相同

**解决方案**:
```bash
# 复制本地密钥到远程环境
scp secret_key user@remote:/path/to/project/

# 或者设置环境变量
export UIN_AES_KEY="your-key-here"
```

### 2. 头像文件不存在
**症状**: "头像文件不存在" 错误
**检查**:
- 头像目录是否存在
- 头像文件是否已上传
- 文件权限是否正确

**解决方案**:
```bash
# 创建头像目录
mkdir -p ./static/avatars/mems

# 上传头像文件
scp -r local_avatars/* user@remote:/path/to/project/static/avatars/mems/

# 设置权限
chmod -R 755 ./static/avatars/
```

### 3. 数据库问题
**症状**: 无法连接数据库或查询失败
**检查**:
- 数据库服务是否运行
- 数据库连接字符串是否正确
- 数据库中是否有成员数据

**解决方案**:
```bash
# 检查PostgreSQL服务
sudo systemctl status postgresql

# 测试数据库连接
psql -h localhost -U username -d database_name

# 检查成员表
SELECT COUNT(*) FROM members;
```

### 4. 环境变量配置
**症状**: 配置不生效
**检查**:
- `.env` 文件是否存在
- 环境变量是否正确设置
- 文件编码是否正确

**解决方案**:
```bash
# 检查.env文件
cat .env

# 检查环境变量
env | grep -E "(DATABASE_URL|AVATAR_ROOT|UIN_AES_KEY)"

# 重新加载环境变量
source .env
```

## 日志分析

### 关键日志标识
- `[GET_AVATAR]`: 头像获取相关日志
- `[CHECK_AVATAR]`: 头像检查相关日志
- `[CRYPTO]`: 加密解密相关日志
- `[CONFIG]`: 配置相关日志

### 日志级别
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息

### 示例日志分析
```
2024-01-01 12:00:00 - api.avatars - INFO - [GET_AVATAR] 开始处理头像请求 - member_id: 1
2024-01-01 12:00:00 - core.crypto - DEBUG - [CRYPTO] 开始解密UIN - salt: abc123
2024-01-01 12:00:00 - core.crypto - ERROR - [CRYPTO] UIN解密失败 - salt: abc123, error: Base64解码失败
```

这表明问题出现在Base64解码阶段，可能是加密数据损坏或密钥不匹配。

## 联系支持
如果以上步骤无法解决问题，请提供：
1. 快速测试脚本的输出
2. 详细调试脚本的日志文件
3. 环境对比的结果
4. 应用运行时的错误日志
