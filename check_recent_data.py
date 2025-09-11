#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查最近几天的数据库数据
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
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ 错误: 未找到MONGODB_URI环境变量")
            return None
            
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ MongoDB Atlas连接成功!")
        return client
        
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return None

def check_database_content(client):
    """
    检查数据库内容
    """
    try:
        db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
        db = client[db_name]
        
        # 列出所有集合
        collections = db.list_collection_names()
        print(f"\n📚 数据库 '{db_name}' 中的集合:")
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"   - {coll}: {count} 条记录")
        
        if 'taiwan_pk10_data' in collections:
            collection = db['taiwan_pk10_data']
            
            # 获取总记录数
            total_count = collection.count_documents({})
            print(f"\n📊 taiwan_pk10_data 集合统计:")
            print(f"   总记录数: {total_count}")
            
            if total_count > 0:
                # 获取最新和最早的记录
                latest = collection.find().sort('timestamp', -1).limit(1)
                earliest = collection.find().sort('timestamp', 1).limit(1)
                
                latest_record = list(latest)
                earliest_record = list(earliest)
                
                if latest_record:
                    print(f"   最新记录时间: {latest_record[0].get('timestamp', 'N/A')}")
                if earliest_record:
                    print(f"   最早记录时间: {earliest_record[0].get('timestamp', 'N/A')}")
                
                # 显示最近5条记录
                print(f"\n📋 最近5条记录:")
                recent_records = collection.find().sort('timestamp', -1).limit(5)
                
                for i, record in enumerate(recent_records, 1):
                    print(f"\n   记录 {i}:")
                    print(f"     _id: {record.get('_id', 'N/A')}")
                    print(f"     期号: {record.get('period', 'N/A')}")
                    print(f"     时间: {record.get('timestamp', 'N/A')}")
                    print(f"     开奖号码: {record.get('winning_numbers', 'N/A')}")
                    if 'data' in record:
                        print(f"     数据: {str(record['data'])[:100]}...")
                
                # 按日期统计最近7天的数据
                taiwan_tz = pytz.timezone('Asia/Taipei')
                now = datetime.now(taiwan_tz)
                
                print(f"\n📅 最近7天数据统计:")
                for i in range(7):
                    date = now - timedelta(days=i)
                    start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_time = start_time + timedelta(days=1)
                    
                    query = {
                        'timestamp': {
                            '$gte': start_time.isoformat(),
                            '$lt': end_time.isoformat()
                        }
                    }
                    
                    day_count = collection.count_documents(query)
                    date_str = date.strftime('%Y-%m-%d (%A)')
                    print(f"   {date_str}: {day_count} 条记录")
            
            else:
                print("   ⚠️  集合为空")
        else:
            print("\n⚠️  未找到 taiwan_pk10_data 集合")
            
    except Exception as e:
        print(f"❌ 检查数据库内容时出错: {e}")

def main():
    """
    主函数
    """
    print("🔍 检查数据库内容...")
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
        # 检查数据库内容
        check_database_content(client)
            
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
    finally:
        # 关闭连接
        if client:
            client.close()
            print("\n🔒 数据库连接已关闭")
    
    print("=" * 50)
    print("🏁 检查完成")

if __name__ == "__main__":
    main()