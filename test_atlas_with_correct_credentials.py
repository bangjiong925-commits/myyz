#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from datetime import datetime
from urllib.parse import quote_plus

def test_atlas_connection():
    """使用用户截图中的正确连接信息测试MongoDB Atlas连接"""
    
    # 根据用户截图中的连接字符串格式
    # mongodb+srv://zhu:<db_password>@cluster0.p4yg8ug.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
    
    print("尝试不同的连接方式...")
    print("=" * 60)
    
    # 方式1: 使用原始密码
    username = "zhu"
    password = "83OmNawYN85nI98i"
    cluster = "cluster0.p4yg8ug.mongodb.net"
    database = "taiwan_pk10"
    
    # 构建连接字符串（根据截图格式）
    mongodb_uri_1 = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=Cluster0"
    
    print(f"方式1 - 连接字符串: {mongodb_uri_1}")
    
    try:
        client = pymongo.MongoClient(mongodb_uri_1, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ 方式1连接成功！")
        
        # 获取数据库
        db = client[database]
        collections = db.list_collection_names()
        print(f"📊 数据库中的集合: {collections}")
        
        # 查询今日数据
        if 'lottery_data' in collections:
            today = datetime.now().strftime('%Y-%m-%d')
            lottery_collection = db['lottery_data']
            today_count = lottery_collection.count_documents({'draw_date': {'$regex': f'^{today}'}})
            print(f"🎲 今日数据条数: {today_count}")
            
            if today_count > 0:
                print("\n📋 最新3条今日数据:")
                latest_data = lottery_collection.find({'draw_date': {'$regex': f'^{today}'}}).sort([('scraped_at', -1)]).limit(3)
                for i, doc in enumerate(latest_data, 1):
                    period = doc.get('period', 'N/A')
                    numbers = doc.get('draw_numbers', [])
                    draw_time = doc.get('draw_time', 'N/A')
                    print(f"{i}. 期号: {period} | 开奖号码: {numbers} | 时间: {draw_time}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 方式1失败: {e}")
    
    # 方式2: URL编码密码
    encoded_password = quote_plus(password)
    mongodb_uri_2 = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority&appName=Cluster0"
    
    print(f"\n方式2 - URL编码密码: {mongodb_uri_2}")
    
    try:
        client = pymongo.MongoClient(mongodb_uri_2, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ 方式2连接成功！")
        
        # 获取数据库
        db = client[database]
        collections = db.list_collection_names()
        print(f"📊 数据库中的集合: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 方式2失败: {e}")
    
    # 方式3: 指定数据库名称
    mongodb_uri_3 = f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0"
    
    print(f"\n方式3 - 指定数据库: {mongodb_uri_3}")
    
    try:
        client = pymongo.MongoClient(mongodb_uri_3, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ 方式3连接成功！")
        
        # 获取数据库
        db = client[database]
        collections = db.list_collection_names()
        print(f"📊 数据库中的集合: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 方式3失败: {e}")
    
    print("\n❌ 所有连接方式都失败了")
    print("\n可能的问题:")
    print("1. 密码已过期或不正确")
    print("2. IP地址未添加到MongoDB Atlas白名单")
    print("3. 用户权限不足")
    print("4. 网络连接问题")
    
    return False

if __name__ == '__main__':
    test_atlas_connection()