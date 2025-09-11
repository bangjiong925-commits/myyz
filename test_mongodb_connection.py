#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB连接测试脚本
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

def test_mongodb_connection():
    """测试MongoDB连接"""
    print("🔍 测试MongoDB连接...")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
    
    print(f"📍 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 MongoDB URI: {mongodb_uri[:50]}...")
    print(f"📚 数据库名: {db_name}")
    print()
    
    try:
        # 连接MongoDB
        print("🔄 正在连接MongoDB...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # 测试连接
        print("🔄 测试服务器连接...")
        client.admin.command('ping')
        print("✅ MongoDB服务器连接成功!")
        
        # 获取数据库
        db = client[db_name]
        
        # 列出所有集合
        collections = db.list_collection_names()
        print(f"📚 数据库 '{db_name}' 中的集合:")
        if collections:
            for coll in collections:
                count = db[coll].count_documents({})
                print(f"   - {coll}: {count} 条记录")
        else:
            print("   - 暂无集合")
        
        # 测试写入权限
        print("\n🔄 测试写入权限...")
        test_collection = db['connection_test']
        test_doc = {
            'test_time': datetime.now(),
            'message': 'MongoDB连接测试成功',
            'test_id': 'connection_test_' + datetime.now().strftime('%Y%m%d_%H%M%S')
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ 写入测试成功! 文档ID: {result.inserted_id}")
        
        # 测试读取权限
        print("🔄 测试读取权限...")
        read_result = test_collection.find_one({'_id': result.inserted_id})
        if read_result:
            print("✅ 读取测试成功!")
        else:
            print("❌ 读取测试失败!")
        
        # 清理测试数据
        test_collection.delete_one({'_id': result.inserted_id})
        print("🧹 测试数据已清理")
        
        client.close()
        print("\n🔒 数据库连接已关闭")
        print("=" * 50)
        print("🎉 MongoDB连接测试完全成功!")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB连接失败: {str(e)}")
        print("=" * 50)
        print("💡 可能的解决方案:")
        print("1. 检查用户名和密码是否正确")
        print("2. 检查网络连接")
        print("3. 检查MongoDB Atlas白名单设置")
        print("4. 检查数据库用户权限")
        return False

if __name__ == "__main__":
    test_mongodb_connection()