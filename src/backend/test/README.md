# 测试目录

本目录包含后端项目的所有测试文件，使用 pytest 框架进行测试。

## 测试文件结构

```
test/
├── README.md                      # 本文件
├── simple_test.py                 # 简单测试示例
├── test_database_connection.py    # 数据库连接测试
└── test_database_service.py       # 数据库服务适配测试
```

## 运行测试

### 环境准备

确保已设置 `DATABASE_URL` 环境变量：

```bash
export DATABASE_URL="postgresql+asyncpg://username:password@host:port/database"
```

### 运行所有测试

```bash
cd src/backend
python -m pytest test/ -v
```

### 运行特定测试文件

```bash
# 运行数据库服务测试
python -m pytest test/test_database_service.py -v

# 运行数据库连接测试
python -m pytest test/test_database_connection.py -v
```

### 运行特定测试类或方法

```bash
# 运行特定测试类
python -m pytest test/test_database_service.py::TestDatabaseService -v

# 运行特定测试方法
python -m pytest test/test_database_service.py::TestDatabaseService::test_database_connection -v
```

## 测试说明

### test_database_service.py

这是数据库服务适配的主要测试文件，包含：

- **TestDatabaseService**: 测试数据库服务的核心功能
  - `test_database_service_creation`: 测试服务创建
  - `test_database_connection`: 测试数据库连接
  - `test_create_tables`: 测试表创建
  - `test_run_migrations`: 测试数据库迁移
  - `test_dependency_injection`: 测试依赖注入系统
  - `test_session_scope`: 测试会话作用域管理

- **TestDatabaseModels**: 测试数据库模型
  - `test_member_model_import`: 测试 Member 模型导入
  - `test_config_model_import`: 测试 Config 模型导入
  - `test_models_metadata`: 测试模型元数据

- **test_full_database_workflow**: 完整的数据库工作流测试

### test_database_connection.py

简单的数据库连接测试，验证数据库是否可用。

## 测试最佳实践

1. **环境隔离**: 使用测试专用的数据库，避免影响开发或生产数据
2. **清理资源**: 每个测试后正确清理数据库连接和服务
3. **异步测试**: 使用 `@pytest.mark.asyncio` 装饰器进行异步测试
4. **Fixture 使用**: 利用 pytest fixture 进行测试数据准备和清理
5. **错误处理**: 测试异常情况和边界条件

## 故障排除

### 常见问题

1. **DATABASE_URL 未设置**
   ```
   pytest.skip("DATABASE_URL environment variable not set")
   ```
   解决方案：设置正确的数据库连接字符串

2. **数据库连接失败**
   检查数据库服务是否运行，连接参数是否正确

3. **导入错误**
   确保在 `src/backend` 目录下运行测试命令

### 调试技巧

- 使用 `-v` 参数查看详细输出
- 使用 `-s` 参数查看 print 输出
- 使用 `--tb=short` 查看简化的错误堆栈
- 使用 `--pdb` 在失败时进入调试器

```bash
python -m pytest test/test_database_service.py -v -s --tb=short
```
