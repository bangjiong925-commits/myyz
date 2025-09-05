#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试远程MongoDB连接配置
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

def test_remote_connection():
    """测试远程MongoDB连接"""
    # 加载.env文件
    load_dotenv()
    
    # 获取环境变量
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
    
    print("===== 远程MongoDB连接测试 =====")
    print(f"连接URI: {mongodb_uri}")
    print(f"数据库名: {db_name}")
    
    if not mongodb_uri:
        print("错误: 未找到MONGODB_URI环境变量")
        return False
    
    try:
        # 尝试连接
        print("正在连接到远程MongoDB...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # 测试连接
        client.admin.command('ping')
        print("✓ 连接成功！")
        
        # 获取数据库
        db = client[db_name]
        
        # 列出集合
        collections = db.list_collection_names()
        print(f"✓ 数据库 '{db_name}' 中的集合: {collections}")
        
        # 如果没有集合，创建一个测试集合
        if not collections:
            print("创建测试集合...")
            test_collection = db['test_connection']
            test_doc = {
                'test': True,
                'message': '远程连接测试成功',
                'timestamp': '2025-01-15'
            }
            result = test_collection.insert_one(test_doc)
            print(f"✓ 测试文档已插入，ID: {result.inserted_id}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 验证MongoDB URI格式")
        print("3. 确认数据库服务器可访问")
        print("4. 检查用户名和密码")
        return False

if __name__ == '__main__':
    success = test_remote_connection()
    if success:
        print("\n🎉 远程MongoDB连接配置成功！")
    else:
        print("\n❌ 远程MongoDB连接配置失败，请检查配置。")