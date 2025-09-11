#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置本地MongoDB数据库
"""

import os
import json
import subprocess
from datetime import datetime
from pymongo import MongoClient

def check_mongodb_installed():
    """
    检查MongoDB是否已安装
    """
    try:
        result = subprocess.run(['mongod', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB已安装")
            return True
        else:
            print("❌ MongoDB未安装")
            return False
    except FileNotFoundError:
        print("❌ MongoDB未安装")
        return False

def install_mongodb_macos():
    """
    在macOS上安装MongoDB
    """
    print("正在安装MongoDB...")
    
    try:
        # 使用Homebrew安装MongoDB
        print("1. 添加MongoDB Homebrew tap...")
        subprocess.run(['brew', 'tap', 'mongodb/brew'], check=True)
        
        print("2. 安装MongoDB Community Edition...")
        subprocess.run(['brew', 'install', 'mongodb-community'], check=True)
        
        print("✅ MongoDB安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ MongoDB安装失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 未找到Homebrew，请先安装Homebrew")
        print("安装命令: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False

def start_mongodb():
    """
    启动MongoDB服务
    """
    try:
        print("正在启动MongoDB服务...")
        
        # 创建数据目录
        data_dir = os.path.expanduser('~/mongodb-data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 启动MongoDB
        cmd = ['mongod', '--dbpath', data_dir, '--port', '27017']
        print(f"启动命令: {' '.join(cmd)}")
        
        # 在后台启动MongoDB
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ MongoDB服务已启动，PID: {process.pid}")
        print(f"数据目录: {data_dir}")
        print("MongoDB运行在: mongodb://localhost:27017")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB启动失败: {e}")
        return False

def test_local_connection():
    """
    测试本地MongoDB连接
    """
    try:
        print("\n正在测试本地MongoDB连接...")
        
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        print("✅ 本地MongoDB连接成功！")
        
        # 创建taiwan_pk10数据库
        db = client['taiwan_pk10']
        
        # 创建测试集合
        test_collection = db['test_data']
        test_doc = {
            'type': 'setup_test',
            'timestamp': datetime.now().isoformat(),
            'message': '本地MongoDB设置成功'
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ 测试数据插入成功，ID: {result.inserted_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 本地MongoDB连接失败: {e}")
        return False

def update_env_for_local():
    """
    更新.env文件使用本地MongoDB
    """
    env_file = '.env'
    local_uri = 'mongodb://localhost:27017/taiwan_pk10'
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('MONGODB_URI='):
                updated_lines.append(f'MONGODB_URI={local_uri}')
                print(f"✅ 已更新MONGODB_URI为本地连接")
            else:
                updated_lines.append(line)
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✅ 已更新 {env_file} 文件")
        
    except Exception as e:
        print(f"❌ 更新.env文件失败: {e}")

def main():
    """
    主函数
    """
    print("=== 设置本地MongoDB数据库 ===")
    print("\n由于远程MongoDB Atlas连接问题，我们将设置本地MongoDB数据库")
    
    # 检查MongoDB是否已安装
    if not check_mongodb_installed():
        print("\n需要安装MongoDB...")
        if not install_mongodb_macos():
            print("❌ MongoDB安装失败，请手动安装")
            print("手动安装步骤:")
            print("1. brew tap mongodb/brew")
            print("2. brew install mongodb-community")
            return
    
    # 启动MongoDB
    print("\n启动MongoDB服务...")
    if not start_mongodb():
        print("❌ MongoDB启动失败")
        print("\n手动启动步骤:")
        print("1. 创建数据目录: mkdir -p ~/mongodb-data")
        print("2. 启动服务: mongod --dbpath ~/mongodb-data --port 27017")
        return
    
    # 等待MongoDB启动
    import time
    print("等待MongoDB启动...")
    time.sleep(3)
    
    # 测试连接
    if test_local_connection():
        # 更新.env文件
        update_env_for_local()
        
        print("\n🎉 本地MongoDB设置完成！")
        print("\n下一步:")
        print("1. 运行数据抓取脚本填充数据")
        print("2. 测试API服务")
        print("3. 确保Railway部署时使用正确的数据库连接")
    else:
        print("❌ 本地MongoDB连接测试失败")

if __name__ == '__main__':
    main()