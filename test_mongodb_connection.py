#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_mongodb_connection():
    """测试MongoDB Atlas连接"""
    mongodb_uri = os.getenv('MONGODB_URI')
    print(f"MongoDB URI: {mongodb_uri}")
    
    try:
        # 创建客户端连接
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # 测试连接
        print("正在测试连接...")
        client.admin.command('ping')
        print("✅ MongoDB Atlas连接成功！")
        
        # 获取数据库信息
        db = client.taiwan_pk10
        collections = db.list_collection_names()
        print(f"数据库中的集合: {collections}")
        
        # 检查数据
        if 'taiwan_pk10_data' in collections:
            collection = db.taiwan_pk10_data
            count = collection.count_documents({})
            print(f"taiwan_pk10_data 集合中的文档数量: {count}")
            
            if count > 0:
                # 获取最新的一条记录
                latest = collection.find().sort('期号', -1).limit(1)
                for doc in latest:
                    print(f"最新记录: 期号 {doc.get('期号')}, 时间 {doc.get('时间')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()