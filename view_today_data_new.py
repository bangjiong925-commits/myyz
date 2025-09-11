#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看今天数据库数据的脚本
使用MongoDB Atlas连接查询今日数据记录
"""

import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import pytz
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_mongodb_connection():
    """
    获取MongoDB连接
    """
    try:
        # 从环境变量获取连接字符串
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ 错误: 未找到MONGODB_URI环境变量")
            return None
            
        print(f"🔗 连接字符串: {mongodb_uri[:50]}...")
        
        # 创建MongoDB客户端
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB Atlas连接成功!")
        
        return client
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB连接失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return None

def get_today_data(client):
    """
    查询今天的数据
    """
    try:
        # 获取数据库和集合
        db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
        db = client[db_name]
        collection = db['taiwan_pk10_data']
        
        # 获取今天的日期范围 (使用台湾时区)
        taiwan_tz = pytz.timezone('Asia/Taipei')
        now = datetime.now(taiwan_tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        print(f"\n📅 查询日期范围: {today_start.strftime('%Y-%m-%d %H:%M:%S')} - {today_end.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 查询今天的数据
        query = {
            'timestamp': {
                '$gte': today_start.isoformat(),
                '$lt': today_end.isoformat()
            }
        }
        
        # 获取数据统计
        total_count = collection.count_documents(query)
        print(f"\n📊 今日数据统计:")
        print(f"   总记录数: {total_count}")
        
        if total_count == 0:
            print("   ⚠️  今天暂无数据记录")
            return
        
        # 获取最新和最早的记录
        latest_record = collection.find(query).sort('timestamp', -1).limit(1)
        earliest_record = collection.find(query).sort('timestamp', 1).limit(1)
        
        latest = list(latest_record)
        earliest = list(earliest_record)
        
        if latest:
            print(f"   最新记录时间: {latest[0].get('timestamp', 'N/A')}")
        if earliest:
            print(f"   最早记录时间: {earliest[0].get('timestamp', 'N/A')}")
        
        # 按期号统计
        pipeline = [
            {'$match': query},
            {'$group': {
                '_id': '$period',
                'count': {'$sum': 1},
                'latest_time': {'$max': '$timestamp'}
            }},
            {'$sort': {'latest_time': -1}},
            {'$limit': 10}
        ]
        
        period_stats = list(collection.aggregate(pipeline))
        if period_stats:
            print(f"\n🎯 最近期号统计 (前10期):")
            for stat in period_stats:
                print(f"   期号 {stat['_id']}: {stat['count']} 条记录, 最新时间: {stat['latest_time']}")
        
        # 显示最新的5条记录详情
        print(f"\n📋 最新5条记录详情:")
        recent_records = collection.find(query).sort('timestamp', -1).limit(5)
        
        for i, record in enumerate(recent_records, 1):
            print(f"\n   记录 {i}:")
            print(f"     期号: {record.get('period', 'N/A')}")
            print(f"     时间: {record.get('timestamp', 'N/A')}")
            print(f"     开奖号码: {record.get('winning_numbers', 'N/A')}")
            if 'data' in record:
                print(f"     数据: {record['data']}")
        
        return total_count
        
    except Exception as e:
        print(f"❌ 查询数据时出错: {e}")
        return None

def main():
    """
    主函数
    """
    print("🚀 开始查询今天的数据库数据...")
    print("=" * 50)
    
    # 显示当前时间
    taiwan_tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(taiwan_tz)
    print(f"📍 当前时间 (台湾): {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # 连接数据库
    client = get_mongodb_connection()
    if not client:
        print("\n❌ 无法连接到数据库，程序退出")
        sys.exit(1)
    
    try:
        # 查询今天的数据
        result = get_today_data(client)
        
        if result is not None:
            print(f"\n✅ 查询完成! 今日共有 {result} 条数据记录")
        else:
            print(f"\n❌ 查询失败")
            
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
    finally:
        # 关闭连接
        if client:
            client.close()
            print("\n🔒 数据库连接已关闭")
    
    print("=" * 50)
    print("🏁 程序执行完成")

if __name__ == "__main__":
    main()