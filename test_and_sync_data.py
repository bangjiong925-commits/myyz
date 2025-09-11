#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MongoDB Atlas连接并同步数据
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# 加载环境变量
load_dotenv()

def test_mongodb_connection():
    """
    测试MongoDB Atlas连接
    """
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
    
    if not mongodb_uri:
        print("❌ 未找到MONGODB_URI环境变量")
        return None, None
    
    print(f"🔗 连接MongoDB Atlas...")
    print(f"URI: {mongodb_uri[:50]}...")
    print(f"数据库: {db_name}")
    
    try:
        # 创建客户端连接
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB Atlas连接成功!")
        
        # 获取数据库
        db = client[db_name]
        
        # 列出现有集合
        collections = db.list_collection_names()
        print(f"📋 现有集合: {collections}")
        
        return client, db
        
    except ConnectionFailure as e:
        print(f"❌ 连接失败: {e}")
        return None, None
    except ServerSelectionTimeoutError as e:
        print(f"❌ 服务器选择超时: {e}")
        return None, None
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return None, None

def sync_sample_data(db):
    """
    同步示例数据到MongoDB Atlas
    """
    print("\n📊 同步示例数据到云端数据库...")
    
    # 今日数据集合
    today_collection = db['today_data']
    
    # 历史数据集合
    history_collection = db['taiwan_pk10_data']
    
    # 生成今日示例数据
    today = datetime.now().strftime('%Y-%m-%d')
    sample_today_data = {
        'date': today,
        'periods': [],
        'last_updated': datetime.now().isoformat()
    }
    
    # 生成10期示例数据
    for period in range(1, 11):
        period_data = {
            'period': f"{today}-{period:03d}",
            'numbers': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # 示例开奖号码
            'time': (datetime.now() - timedelta(minutes=30-period*3)).strftime('%H:%M:%S'),
            'status': 'completed'
        }
        sample_today_data['periods'].append(period_data)
    
    try:
        # 插入或更新今日数据
        today_collection.replace_one(
            {'date': today},
            sample_today_data,
            upsert=True
        )
        print(f"✅ 今日数据已同步 ({len(sample_today_data['periods'])}期)")
        
        # 生成历史数据
        historical_dates = []
        for i in range(1, 8):  # 过去7天
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            historical_dates.append(date)
        
        for date in historical_dates:
            # 检查是否已存在
            if history_collection.find_one({'date': date}):
                continue
                
            historical_data = {
                'date': date,
                'periods': [],
                'last_updated': datetime.now().isoformat()
            }
            
            # 每天10期数据
            for period in range(1, 11):
                period_data = {
                    'period': f"{date}-{period:03d}",
                    'numbers': [i % 10 + 1 for i in range(period, period + 10)],  # 示例号码
                    'time': f"{9 + period}:00:00",
                    'status': 'completed'
                }
                historical_data['periods'].append(period_data)
            
            history_collection.insert_one(historical_data)
        
        print(f"✅ 历史数据已同步 ({len(historical_dates)}天)")
        
        # 显示数据统计
        today_count = today_collection.count_documents({})
        history_count = history_collection.count_documents({})
        
        print(f"\n📈 数据统计:")
        print(f"  - 今日数据: {today_count} 条记录")
        print(f"  - 历史数据: {history_count} 条记录")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据同步失败: {e}")
        return False

def test_api_data(db):
    """
    测试API数据查询
    """
    print("\n🔍 测试API数据查询...")
    
    try:
        # 测试今日数据
        today = datetime.now().strftime('%Y-%m-%d')
        today_data = db['today_data'].find_one({'date': today})
        
        if today_data:
            print(f"✅ 今日数据查询成功: {len(today_data.get('periods', []))}期")
        else:
            print("⚠️ 未找到今日数据")
        
        # 测试历史数据
        history_count = db['taiwan_pk10_data'].count_documents({})
        print(f"✅ 历史数据查询成功: {history_count}天记录")
        
        # 测试最新一期数据
        latest = db['today_data'].find_one(
            {'date': today},
            sort=[('last_updated', -1)]
        )
        
        if latest and latest.get('periods'):
            latest_period = latest['periods'][-1]
            print(f"✅ 最新一期: {latest_period['period']} - {latest_period['numbers']}")
        
        return True
        
    except Exception as e:
        print(f"❌ API数据测试失败: {e}")
        return False

def main():
    print("=== MongoDB Atlas 连接测试与数据同步 ===")
    print("注意: 只使用云端MongoDB Atlas，不涉及任何本地数据库")
    
    # 测试连接
    client, db = test_mongodb_connection()
    
    if not client or not db:
        print("\n❌ 无法连接到MongoDB Atlas，请检查连接字符串")
        sys.exit(1)
    
    try:
        # 同步数据
        if sync_sample_data(db):
            print("\n✅ 数据同步完成")
        else:
            print("\n❌ 数据同步失败")
            sys.exit(1)
        
        # 测试API数据
        if test_api_data(db):
            print("\n✅ API数据测试通过")
        else:
            print("\n❌ API数据测试失败")
        
        print("\n🎉 所有测试完成!")
        print("\n下一步:")
        print("1. 重启API服务器")
        print("2. 测试API端点: /api/today-data 和 /api/taiwan-pk10-data")
        print("3. 重新部署Railway服务")
        
    finally:
        client.close()

if __name__ == "__