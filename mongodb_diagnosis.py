#!/usr/bin/env python3
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import urllib.parse

# 加载环境变量
load_dotenv()

# 获取连接信息
mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')

print("MongoDB Atlas 连接诊断")
print("=" * 50)
print(f"数据库名: {db_name}")
print(f"完整URI: {mongodb_uri}")
print()

# 解析URI获取详细信息
if mongodb_uri:
    try:
        # 解析连接字符串
        if '@' in mongodb_uri:
            auth_part = mongodb_uri.split('://')[1].split('@')[0]
            if ':' in auth_part:
                username, password = auth_part.split(':', 1)
                print(f"用户名: {username}")
                print(f"密码: {password}")
                print(f"密码长度: {len(password)}")
                print()
        
        # 尝试不同的连接超时设置
        print("尝试连接 (5秒超时)...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # 测试连接
        print("执行 ping 命令...")
        result = client.admin.command('ping')
        print(f"Ping 结果: {result}")
        
        print("连接成功！")
        
        # 获取数据库信息
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"集合列表: {collections}")
        
        client.close()
        
    except Exception as e:
        print(f"连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        
        # 尝试更长的超时时间
        try:
            print("\n尝试更长超时时间 (30秒)...")
            client2 = MongoClient(mongodb_uri, serverSelectionTimeoutMS=30000)
            result2 = client2.admin.command('ping')
            print(f"长超时 Ping 结果: {result2}")
            client2.close()
        except Exception as e2:
            print(f"长超时也失败: {e2}")
else:
    print("错误: 未找到 MONGODB_URI 环境变量")

print("\n诊断完成")