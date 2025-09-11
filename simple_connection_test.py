#!/usr/bin/env python3
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

# 获取连接信息
mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')

print("MongoDB Atlas Connection Test")
print(f"Database: {db_name}")
print(f"URI: {mongodb_uri[:30]}...")

try:
    # 连接数据库
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("SUCCESS: Connected to MongoDB Atlas")
    
    # 获取数据库和集合信息
    db = client[db_name]
    collections = db.list_collection_names()
    print(f"Collections: {collections}")
    
    # 查询今日数据
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Today: {today}")
    
    total_records = 0
    for coll_name in collections:
        coll = db[coll_name]
        count = coll.count_documents({})
        total_records += count
        print(f"{coll_name}: {count} records")
        
        # 显示最新的一条记录
        latest = coll.find_one({}, sort=[('_id', -1)])
        if latest:
            # 移除_id字段
            if '_id' in latest:
                del latest['_id']
            print(f"  Latest: {latest}")
    
    print(f"Total records: {total_records}")
    client.close()
    print("Connection closed successfully")
    
except Exception as e:
    print(f"ERROR: {e}")