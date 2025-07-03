#!/usr/bin/env python3
"""
环境检查脚本 - 验证部署环境是否正确配置
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple

def check_command(command: str) -> Tuple[bool, str]:
    """检查命令是否可用"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Command not found"

def check_file_exists(file_path: str) -> Tuple[bool, str]:
    """检查文件是否存在"""
    path = Path(file_path)
    if path.exists():
        if path.is_file():
            return True, f"File exists ({path.stat().st_size} bytes)"
        else:
            return False, "Path exists but is not a file"
    else:
        return False, "File not found"

def check_directory_exists(dir_path: str) -> Tuple[bool, str]:
    """检查目录是否存在"""
    path = Path(dir_path)
    if path.exists():
        if path.is_dir():
            file_count = len(list(path.iterdir()))
            return True, f"Directory exists ({file_count} items)"
        else:
            return False, "Path exists but is not a directory"
    else:
        return False, "Directory not found"

def check_json_file(file_path: str) -> Tuple[bool, str]:
    """检查JSON文件格式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'mems' in data and isinstance(data['mems'], list):
            member_count = len(data['mems'])
            return True, f"Valid JSON with {member_count} members"
        else:
            return False, "JSON format invalid (missing 'mems' array)"
    except FileNotFoundError:
        return False, "File not found"
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_avatar_files(avatar_dir: str, json_file: str) -> Tuple[bool, str]:
    """检查头像文件是否完整"""
    try:
        # 读取成员数据
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'mems' not in data:
            return False, "Invalid JSON format"
        
        members = data['mems']
        avatar_path = Path(avatar_dir)
        
        if not avatar_path.exists():
            return False, "Avatar directory not found"
        
        missing_avatars = []
        existing_avatars = 0
        
        for member in members:
            uin = member.get('uin')
            if uin:
                avatar_file = avatar_path / f"{uin}.webp"
                if avatar_file.exists():
                    existing_avatars += 1
                else:
                    missing_avatars.append(str(uin))
        
        total_members = len(members)
        if missing_avatars:
            missing_count = len(missing_avatars)
            return False, f"{existing_avatars}/{total_members} avatars found, missing {missing_count}"
        else:
            return True, f"All {total_members} avatar files found"
            
    except Exception as e:
        return False, f"Error checking avatars: {e}"

def print_check_result(name: str, success: bool, message: str):
    """打印检查结果"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {name}: {message}")

def main():
    """主检查函数"""
    print("=" * 60)
    print("VRC Division 环境检查")
    print("=" * 60)
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"项目根目录: {project_root}")
    print()
    
    # 检查系统命令
    print("🔧 系统工具检查:")
    print("-" * 30)
    
    commands = [
        ("python3", "Python 3"),
        ("python", "Python"),
        ("node", "Node.js"),
        ("npm", "NPM"),
        ("uv", "UV Package Manager"),
        ("psql", "PostgreSQL Client")
    ]
    
    for cmd, name in commands:
        success, message = check_command(cmd)
        print_check_result(name, success, message)
    
    print()
    
    # 检查项目文件结构
    print("📁 项目文件结构检查:")
    print("-" * 30)
    
    files_to_check = [
        ("src/frontend/package.json", "前端配置文件"),
        ("src/backend/pyproject.toml", "后端配置文件"),
        ("src/backend/run.py", "后端启动脚本"),
        ("src/backend/.env", "后端环境配置"),
        ("scripts/dev.sh", "开发脚本 (Linux)"),
        ("scripts/dev.bat", "开发脚本 (Windows)"),
        ("scripts/prod.sh", "生产脚本 (Linux)"),
        ("scripts/prod.bat", "生产脚本 (Windows)"),
    ]
    
    for file_path, description in files_to_check:
        full_path = project_root / file_path
        success, message = check_file_exists(str(full_path))
        print_check_result(description, success, message)
    
    print()
    
    # 检查数据文件
    print("📊 数据文件检查:")
    print("-" * 30)
    
    # QQ群成员JSON文件
    json_file = project_root / "src/backend/static/qq_group_937303337_members.json"
    success, message = check_json_file(str(json_file))
    print_check_result("QQ群成员数据", success, message)
    
    # 头像目录
    avatar_dir = project_root / "src/backend/static/avatars/mems"
    success, message = check_directory_exists(str(avatar_dir))
    print_check_result("头像文件目录", success, message)
    
    # 头像文件完整性
    if json_file.exists() and avatar_dir.exists():
        success, message = check_avatar_files(str(avatar_dir), str(json_file))
        print_check_result("头像文件完整性", success, message)
    
    print()
    
    # 检查环境配置
    print("⚙️  环境配置检查:")
    print("-" * 30)
    
    env_file = project_root / "src/backend/.env"
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            required_vars = [
                "DATABASE_URL",
                "AVATAR_ROOT", 
                "HOST",
                "PORT",
                "DEBUG"
            ]
            
            missing_vars = []
            for var in required_vars:
                if f"{var}=" not in env_content:
                    missing_vars.append(var)
            
            if missing_vars:
                print_check_result("环境变量配置", False, f"缺少变量: {', '.join(missing_vars)}")
            else:
                print_check_result("环境变量配置", True, "所有必需变量已配置")
                
        except Exception as e:
            print_check_result("环境变量配置", False, f"读取失败: {e}")
    else:
        print_check_result("环境变量配置", False, ".env 文件不存在")
    
    print()
    print("=" * 60)
    print("检查完成！")
    print()
    print("📋 下一步操作建议:")
    print("1. 如有 ❌ FAIL 项目，请根据部署指南进行修复")
    print("2. 确保 PostgreSQL 数据库已启动并可连接")
    print("3. 运行 scripts/install-deps.sh 安装依赖")
    print("4. 运行 scripts/dev.sh 启动开发环境")
    print("=" * 60)

if __name__ == "__main__":
    main()
