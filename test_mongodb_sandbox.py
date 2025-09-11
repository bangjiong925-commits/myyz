#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MongoDB Atlas沙盒集群连接
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import sys
from datetime import datetime

# 加载环境变量
load_dotenv()

def test_mongodb_connection():
    """
    测试MongoDB连接
    """
    print("=== MongoDB Atlas 沙盒集群连接测试 ===")
    
    # 从环境变量获取连接字符串
    mongodb_uri = os.getenv('MONGODB_URI')
    print(f"环境变量MONGODB_URI: {mongodb_uri}")
    
    # 如果环境变量为空或指向本地，使用MongoDB Atlas沙盒集群
    if not mongodb_uri or 'localhost' in mongodb_uri:
        # 使用MongoDB Atlas免费沙盒集群 (M0 - 512MB免费)
        mongodb_uri = "mongodb+srv://sandbox:sandbox123@cluster0-sandbox.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"
        print(f"使用沙盒集群: {mongodb_uri}")
    
    try:
        print("\n正在连接MongoDB Atlas...")
        
        # 创建客户端连接，设置较短的超时时间
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=15000,  # 15秒超时
            connectTimeoutMS=10000,          # 10秒连接超时
            socketTimeoutMS=10000            # 10秒socket超时
        )
        
        print("正在测试连接...")
        # 测试连接
        result = client.admin.command('ping')
        print(f"✅ MongoDB Atlas连接成功！Ping结果: {result}")
        
        # 获取数据库
        db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
        db = client[db_name]
        print(f"\n使用数据库: {db_name}")
        
        # 列出所有集合
        collections = db.list_collection_names()
        print(f"数据库中的集合: {collections}")
        
        # 如果没有集合，创建一个测试集合
        if not collections:
            print("\n数据库为空，创建测试集合...")
            test_collection = db['test_data']
            
            # 插入测试数据
            test_doc = {
                'type': 'connection_test',
                'timestamp': datetime.now().isoformat(),
                'message': 'MongoDB Atlas连接测试成功',
                'status': 'active'
            }
            
            result = test_collection.insert_one(test_doc)
            print(f"✅ 测试数据插入成功，ID: {result.inserted_id}")
            
            # 查询测试数据
            found_doc = test_collection.find_one({'_id': result.inserted_id})
            print(f"✅ 查询测试数据成功: {found_doc}")
            
        else:
            # 检查现有集合的数据
            for collection_name in collections[:3]:  # 只检查前3个集合
                collection = db[collection_name]
                count = collection.count_documents({})
                print(f"集合 '{collection_name}' 包含 {count} 条记录")
                
                if count > 0:
                    # 显示一条示例数据
                    sample = collection.find_one()
                    print(f"示例数据: {sample}")
        
        print("\n✅ MongoDB Atlas连接测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        
        # 提供解决方案
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 确认MongoDB Atlas集群正在运行")
        print("3. 检查用户名和密码是否正确")
        print("4. 确认IP地址已添加到访问白名单")
        print("5. 检查连接字符串格式是否正确")
        
        return False

def main():
    """
    主函数
    """
    print("开始MongoDB Atlas连接测试...\n")
    
    success = test_mongodb_connection()
    
    if success:
        print("\n🎉 数据库连接成功！可以开始数据同步。")
        sys.exit(0)
    else:
        print("\n❌ 数据库连接失败，请检查配置。")
        sys.exit(1)

if __name__ == '__main__':
    main(