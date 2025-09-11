#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新MongoDB Atlas密码连接
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient

def test_new_password_connection():
    """
    测试新密码的MongoDB Atlas连接
    """
    print("=" * 60)
    print("MongoDB Atlas 新密码连接测试")
    print("=" * 60)
    
    # 使用新密码的连接字符串
    mongodb_uri = "mongodb+srv://zhu:VQup9KicVurnQioj@cluster0.p4yg8ug.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"
    db_name = "taiwan_pk10"
    
    print(f"数据库名称: {db_name}")
    print(f"用户名: zhu")
    print(f"新密码: VQup9KicVurnQioj")
    print(f"集群: cluster0.p4yg8ug.mongodb.net")
    print()
    
    try:
        # 连接MongoDB Atlas
        print("正在连接MongoDB Atlas...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB Atlas连接成功!")
        
        # 获取数据库
        db = client[db_name]
        
        # 获取集合列表
        collections = db.list_collection_names()
        print(f"\n数据库中的集合: {collections}")
        
        # 获取今日日期
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\n查询今日数据 ({today}):")
        print("-" * 40)
        
        # 查询各个集合的今日数据
        total_today_records = 0
        
        for collection_name in collections:
            collection = db[collection_name]
            
            # 查询今日数据
            today_query = {
                "$or": [
                    {"timestamp": {"$regex": f"^{today}"}},
                    {"date": {"$regex": f"^{today}"}},
                    {"created_at": {"$regex": f"^{today}"}}
                ]
            }
            
            today_count = collection.count_documents(today_query)
            total_count = collection.count_documents({})
            
            print(f"集合 '{collection_name}':")
            print(f"  - 今日记录数: {today_count}")
            print(f"  - 总记录数: {total_count}")
            
            total_today_records += today_count
            
            # 显示今日数据的前3条记录
            if today_count > 0:
                print(f"  - 今日数据示例:")
                sample_docs = list(collection.find(today_query).limit(3))
                for i, doc in enumerate(sample_docs, 1):
                    # 移除_id字段以便更好显示
                    if '_id' in doc:
                        del doc['_id']
                    print(f"    {i}. {doc}")
            print()
        
        print(f"📊 统计信息:")
        print(f"  - 总集合数: {len(collections)}")
        print(f"  - 今日总记录数: {total_today_records}")
        
        # 如果有lottery_data集合，显示更详细的信息
        if 'lottery_data' in collections:
            lottery_collection = db['lottery_data']
            print(f"\n🎲 彩票数据详细信息:")
            
            # 查询今日最新的几条记录
            latest_records = list(lottery_collection.find(today_query).sort("_id", -1).limit(5))
            
            if latest_records:
                print(f"  今日最新5条记录:")
                for i, record in enumerate(latest_records, 1):
                    period = record.get('period', 'N/A')
                    numbers = record.get('numbers', [])
                    timestamp = record.get('timestamp', 'N/A')
                    print(f"    {i}. 期号: {period}, 号码: {numbers}, 时间: {timestamp}")
            else:
                print("  今日暂无彩票数据")
        
        client.close()
        print("\n✅ 测试完成，连接已关闭")
        
    except Exception as e:
        print(f"❌ 连接或查询失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        return False
    
    return True

if __name__ == '__main__':
    success = test_new_password_connection()
    if success:
        print("\n🎉 新密码连接测试通过!")
    else:
        print("\n❌ 新密码连接测试失败")
        sys.exit(1)