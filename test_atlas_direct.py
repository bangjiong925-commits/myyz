#!/usr/bin/env python3
from pymongo import MongoClient
import sys

# 直接测试MongoDB Atlas连接
atlas_uri = "mongodb+srv://twpk_demo:twpk123456@cluster0.4zhkx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"

print("=== MongoDB Atlas 直接连接测试 ===")
print(f"连接字符串: {atlas_uri}")

try:
    print("正在连接...")
    client = MongoClient(atlas_uri, serverSelectionTimeoutMS=10000)
    
    print("正在测试连接...")
    client.admin.command('ping')
    print("✅ MongoDB Atlas连接成功！")
    
    # 测试数据库
    db = client['taiwan_pk10']
    collections = db.list_collection_names()
    print(f"数据库 'taiwan_pk10' 中的集合: {collections}")
    
    # 测试插入一条数据
    test_collection = db['test_connection']
    test_doc = {'test': True, 'timestamp': '2025-09-10'}
    result = test_collection.insert_one(test_doc)
    print(f"测试插入成功，ID: {result.inserted_id}")
    
    # 删除测试数据
    test_collection.delete_one({'_id': result.inserted_id})
    print("测试数据已清理")
    
except Exception as e:
    print(f"❌ 连接失败: {e}")
    sys.exit(1)

print("\n测试完成！MongoDB Atlas连接正常。")