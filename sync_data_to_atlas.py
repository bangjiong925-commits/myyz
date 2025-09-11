#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步数据到MongoDB Atlas
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

# 加载环境变量
load_dotenv()

def create_sample_data():
    """
    创建示例数据
    """
    print("📊 创建示例数据...")
    
    # 今日数据
    today = datetime.now().strftime('%Y-%m-%d')
    today_data = {
        'date': today,
        'periods': [],
        'last_updated': datetime.now().isoformat()
    }
    
    # 生成10期今日数据
    for period in range(1, 11):
        period_time = datetime.now() - timedelta(minutes=30-period*3)
        period_data = {
            'period': f"{today}-{period:03d}",
            'numbers': [(i + period) % 10 + 1 for i in range(10)],  # 示例开奖号码
            'time': period_time.strftime('%H:%M:%S'),
            'status': 'completed'
        }
        today_data['periods'].append(period_data)
    
    # 历史数据
    history_data = []
    for i in range(1, 8):  # 过去7天
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_data = {
            'date': date,
            'periods': [],
            'last_updated': datetime.now().isoformat()
        }
        
        # 每天10期数据
        for period in range(1, 11):
            period_data = {
                'period': f"{date}-{period:03d}",
                'numbers': [(i + period + j) % 10 + 1 for j in range(10)],
                'time': f"{9 + period}:00:00",
                'status': 'completed'
            }
            day_data['periods'].append(period_data)
        
        history_data.append(day_data)
    
    return today_data, history_data

def sync_to_mongodb():
    """
    同步数据到MongoDB Atlas
    """
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
    
    if not mongodb_uri:
        print("❌ 未找到MONGODB_URI环境变量")
        return False
    
    print(f"🔗 连接MongoDB Atlas: {mongodb_uri[:50]}...")
    
    try:
        # 连接数据库
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        # 测试连接
        client.admin.command('ping')
        print("✅ 连接成功!")
        
        # 创建示例数据
        today_data, history_data = create_sample_data()
        
        # 同步今日数据
        today_collection = db['today_data']
        today_collection.replace_one(
            {'date': today_data['date']},
            today_data,
            upsert=True
        )
        print(f"✅ 今日数据已同步: {today_data['date']} ({len(today_data['periods'])}期)")
        
        # 同步历史数据
        history_collection = db['taiwan_pk10_data']
        for day_data in history_data:
            history_collection.replace_one(
                {'date': day_data['date']},
                day_data,
                upsert=True
            )
        
        print(f"✅ 历史数据已同步: {len(history_data)}天记录")
        
        # 验证数据
        today_count = today_collection.count_documents({})
        history_count = history_collection.count_documents({})
        
        print(f"\n📈 数据库统计:")
        print(f"  - 今日数据集合: {today_count} 条记录")
        print(f"  - 历史数据集合: {history_count} 条记录")
        
        # 显示最新数据
        latest_today = today_collection.find_one({'date': today_data['date']})
        if latest_today and latest_today.get('periods'):
            latest_period = latest_today['periods'][-1]
            print(f"  - 最新一期: {latest_period['period']} - {latest_period['numbers']}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        return False

def main():
    print("=== 数据同步到MongoDB Atlas ===")
    print("注意: 只使用云端MongoDB Atlas，不涉及本地数据库")
    
    if sync_to_mongodb():
        print("\n🎉 数据同步完成!")
        print("\n下一步:")
        print("1. 重启API服务器")
        print("2. 测试API端点")
        print("3. 部署到Railway")
    else:
        print("\n❌ 数据同步失败")
        sys.exit(1)

if __name__ == "__main__":
    main()