#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MongoDB Atlas连接 - 使用新密码zhu451277
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime
import traceback

def load_env_file():
    """加载.env文件中的环境变量"""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✓ 已加载环境变量文件: {env_path}")
    else:
        print(f"⚠️ 环境变量文件不存在: {env_path}")

def test_mongodb_connection():
    """测试MongoDB Atlas连接"""
    print("\n=== MongoDB Atlas 连接测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载环境变量
    load_env_file()
    
    # 获取连接字符串
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
    
    if not mongodb_uri:
        print("❌ 错误: 未找到MONGODB_URI环境变量")
        return False
    
    # 显示连接信息（隐藏密码）
    safe_uri = mongodb_uri.replace('zhu451277', '***')
    print(f"连接字符串: {safe_uri}")
    print(f"数据库名称: {db_name}")
    
    try:
        print("\n正在连接MongoDB Atlas...")
        
        # 创建客户端连接
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # 测试连接
        print("正在验证服务器连接...")
        client.admin.command('ping')
        print("✓ 服务器连接成功")
        
        # 获取数据库
        db = client[db_name]
        print(f"✓ 数据库 '{db_name}' 连接成功")
        
        # 列出集合
        collections = db.list_collection_names()
        print(f"✓ 数据库中的集合: {collections}")
        
        # 测试数据操作
        if 'pk10_data' in collections:
            collection = db['pk10_data']
            count = collection.count_documents({})
            print(f"✓ pk10_data集合中共有 {count} 条记录")
            
            # 获取最新的一条记录
            latest_record = collection.find_one(sort=[('_id', -1)])
            if latest_record:
                print(f"✓ 最新记录时间: {latest_record.get('timestamp', '未知')}")
        
        # 测试写入权限
        test_collection = db['connection_test']
        test_doc = {
            'test_time': datetime.now(),
            'test_message': '连接测试成功',
            'password_updated': 'zhu451277'
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✓ 写入测试成功，文档ID: {result.inserted_id}")
        
        # 清理测试数据
        test_collection.delete_one({'_id': result.inserted_id})
        print("✓ 测试数据已清理")
        
        client.close()
        print("\n🎉 MongoDB Atlas连接测试完全成功！")
        print("新密码 zhu451277 工作正常")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ 连接失败: {e}")
        print("请检查网络连接和MongoDB Atlas集群状态")
        return False
        
    except OperationFailure as e:
        print(f"❌ 操作失败: {e}")
        print("可能是认证失败，请检查用户名和密码")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)