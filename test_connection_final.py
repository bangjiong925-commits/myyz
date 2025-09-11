#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from urllib.parse import quote_plus
import os
from datetime import datetime, timedelta

def test_mongodb_connection():
    print("="*60)
    print("MongoDB Atlas 连接诊断测试")
    print("="*60)
    
    # 直接使用提供的凭据
    username = "zhu"
    password = "0ghZG7yrF3lqgDuV"
    cluster = "cluster0.p4yg8ug.mongodb.net"
    database = "taiwan_pk10"
    
    # URL编码密码以防特殊字符问题
    encoded_password = quote_plus(password)
    
    # 构建连接字符串
    connection_string = f"mongodb+srv://{username}:{encoded_password}@{cluster}/{database}?retryWrites=true&w=majority"
    
    print(f"用户名: {username}")
    print(f"密码: {password}")
    print(f"集群: {cluster}")
    print(f"数据库: {database}")
    print(f"连接字符串: {connection_string[:50]}...")
    print()
    
    try:
        print("正在连接MongoDB Atlas...")
        
        # 创建客户端连接
        client = pymongo.MongoClient(
            connection_string,
            serverSelectionTimeoutMS=10000,  # 10秒超时
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # 测试连接
        print("正在验证连接...")
        client.admin.command('ping')
        print("✅ 连接成功！")
        
        # 获取数据库
        db = client[database]
        
        # 列出所有集合
        print("\n📋 数据库中的集合:")
        collections = db.list_collection_names()
        for i, collection in enumerate(collections, 1):
            print(f"  {i}. {collection}")
        
        if not collections:
            print("  ⚠️ 数据库中没有集合")
            return
        
        # 检查今日数据
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\n📅 查询今日数据 ({today}):")
        
        for collection_name in collections:
            collection = db[collection_name]
            
            # 获取总记录数
            total_count = collection.count_documents({})
            print(f"\n  📊 集合 '{collection_name}':")
            print(f"    总记录数: {total_