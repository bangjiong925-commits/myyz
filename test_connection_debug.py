#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 加载环境变量
load_dotenv()

def test_connection():
    """测试MongoDB Atlas连接"""
    
    # 从环境变量获取连接信息
    mongodb_uri = os.getenv('MONGODB_URI')
    print(f"原始连接字符串: {mongodb_uri}")
    
    # 手动构建连接字符串，确保用户名和密码正确编码
    username = "zhu"
    password = "83OmNawYN85nI98i"
    cluster = "cluster0.p4yg8ug.mongodb.net"
    database = "taiwan_pk10"
    
    # URL编码用户名和密码
    encoded_username = quote_plus(username)
    encoded_password = quote_plus(password)
    
    # 构建新的连接字符串
    new_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster}/{database}?retryWrites=true&w=majority"
    print(f"新构建的连接字符串: {new_uri}")
    
    try:
        print("\n尝试使用原始连接字符串...")
        client1 = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client1.admin.command('ping')
        print("原始连接字符串成功！")
        client1.close()
    except Exception as e:
        print(f"原始连接字符串失败: {e}")
    
    try:
        print("\n尝试使用新构建的连接字符串...")
        client2 = MongoClient(new_uri, serverSelectionTimeoutMS=5000)
        client2.admin.command('ping')
        print("新连接字符串成功！")
        
        # 如果连接成功，查看数据库信息
        db = client2[database]
        collections = db.list_collection_names()
        print(f"数据库中的集合: {collections}")
        
        # 查看今天的数据
        if 'lottery_data' in collections:
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            today_count = db['lottery_data'].count_documents({'draw_date': {'$regex': f'^{today}'}})
            print(f"今天({today})的数据条数: {today_count}")
            
            if today_count > 0:
                # 显示最新的几条数据
                latest_data = db['lottery_data'].find({'draw_date': {'$regex': f'^{today}'}}).sort([('scraped_at', -1)]).limit(3)
                print("\n最新3条今日数据:")
                for i, doc in enumerate(latest_data, 1):
                    print(f"{i}. 期号: {doc.get('period', 'N/A')}, 开奖号码: {doc.get('draw_numbers', [])}, 开奖时间: {doc.get('draw_time', 'N/A')}")
        
        client2.close()
        
    except Exception as e:
        print(f"新连接字符串失败: {e}")

if __name__ == '__main__':
    test_connection()