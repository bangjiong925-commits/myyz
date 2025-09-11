#!/usr/bin/env python3
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 直接使用MongoDB Atlas连接字符串进行测试
mongodb_uri = "mongodb+srv://twpk_demo:twpk123456@cluster0.4zhkx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"
print(f"使用硬编码连接字符串测试...")

# 也尝试从环境变量读取
env_uri = os.getenv('MONGODB_URI')
print(f"环境变量MONGODB_URI: {env_uri}")

# 如果环境变量存在且不是本地连接，使用环境变量
if env_uri and 'localhost' not in env_uri:
    mongodb_uri = env_uri
    print(f"使用环境变量连接字符串")
else:
    print(f"使用硬编码连接字符串")
print(f"测试连接: {mongodb_uri}")

try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ MongoDB连接成功！")
    
    # 测试数据库
    db = client['taiwan_pk10']
    collections = db.list_collection_names()
    print(f"数据库集合: {collections}")
    
except Exception as e:
    print(f"❌ 连接失败: {e}")