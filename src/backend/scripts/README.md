# QQ群成员数据导入脚本（异步版本）

## 功能说明

`import_group_json.py` 脚本用于将QQ群成员JSON数据导入到PostgreSQL数据库中。该脚本使用项目的异步数据库架构，完全兼容现有的数据库服务和依赖注入系统。

## 架构特点

### 异步数据库架构
- 使用 `DatabaseService` 和 `DatabaseServiceFactory` 
- 支持 PostgreSQL + asyncpg 异步驱动
- 集成项目的依赖注入系统 (`services.deps`)
- 使用 `session_scope()` 进行事务管理

### 安全特性
- **UIN加密**: AES-256-GCM加密存储QQ号
- **随机盐值**: 每个成员独立的16字符随机盐值
- **头像哈希**: 安全的头像文件标识生成
- **自动事务管理**: 异常时自动回滚

## 使用方法

### 1. 基本用法

```bash
cd src/backend
python scripts/import_group_json.py <json_file_path>
```

### 2. 示例

```bash
# 导入示例数据
python scripts/import_group_json.py static/qq_group_members.example.json

# 导入真实群数据
python scripts/import_group_json.py static/qq_group_937303337_members.json
```

## JSON文件格式

脚本支持标准的QQ群成员导出JSON格式：

```json
{
  "ec": 0,
  "errcode": 0,
  "em": "",
  "cache": 0,
  "adm_num": 0,
  "levelname": {...},
  "mems": [
    {
      "uin": 1000000001,
      "role": 2,
      "g": 1,
      "join_time": 1729351588,
      "last_speak_time": 1750850645,
      "lv": {
        "point": 1234,
        "level": 4,
        "levelname": "活跃"
      },
      "card": "示例用户1",
      "nick": "ExampleUser1",
      "qage": 365,
      "tags": "",
      "role_name": "成员"
    }
  ]
}
```

## 数据处理

### 字段映射

- `uin` → 加密存储为 `uin_encrypted`
- `card` → `group_nick` (群昵称)
- `nick` → `qq_nick` (QQ昵称)
- `role` → `role` (角色：0=群主, 1=管理员, 2=群员)
- `join_time` → `join_time` (Unix时间戳转换为datetime)
- `last_speak_time` → `last_speak_time`
- `lv.point` → `level_point`
- `lv.level` → `level_value`
- `qage` → `q_age`

### 显示名称逻辑

优先级：`card` (群昵称) > `nick` (QQ昵称) > `用户{uin}`

## 验证脚本

### 验证导入数据（异步版本）

```bash
python scripts/verify_import.py
```

### 测试加密解密（异步版本）

```bash
python scripts/test_crypto.py
```

## 技术实现

### 异步数据库操作

```python
# 初始化数据库服务
factory = DatabaseServiceFactory()
db_service = factory.create(settings.database_url)
set_database_service(db_service)

# 使用异步会话
async with session_scope() as session:
    # 数据库操作
    await session.exec(delete(Member))
    session.add_all(members)
    # 自动提交和错误回滚
```

### 依赖注入集成

- 使用 `set_database_service()` 设置全局服务
- 通过 `session_scope()` 获取异步会话
- 自动处理事务提交和回滚
- 完整的资源清理

## 注意事项

1. **数据库清空**: 脚本会清空现有的成员数据后再导入新数据
2. **异步架构**: 完全使用项目的异步数据库架构
3. **环境配置**: 确保 `.env` 文件中的数据库配置正确
4. **权限要求**: 需要数据库写入权限
5. **资源管理**: 自动清理数据库连接和服务

## 错误处理

脚本包含完整的错误处理：

- JSON文件格式验证
- 数据库连接检查
- 单个成员数据处理异常捕获
- 自动事务回滚
- 详细的进度和错误信息输出
- 资源清理保证

## 输出示例

```
🔄 开始导入成员数据: static/qq_group_937303337_members.json
✅ 成功读取JSON文件
📊 找到 78 个成员
✅ 成功处理 78 个成员数据
🗑️  清空现有成员数据...
💾 插入新成员数据...
🎉 成功导入 78 个成员到数据库
DEBUG | services.database.service:teardown:108 - Tearing down database
```

## 与项目集成

该脚本完全集成到项目的异步架构中：

- 使用相同的数据库服务层
- 遵循相同的依赖注入模式
- 兼容现有的数据模型
- 支持相同的配置系统
- 使用相同的加密服务
