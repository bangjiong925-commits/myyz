#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_today_data():
    """检查数据库中的今日数据"""
    
    # 获取MongoDB连接信息
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'lottery_db')
    
    if not mongodb_uri:
        print("错误: 未找到MONGODB_URI环境变量")
        return
    
    try:
        # 连接MongoDB
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        # 获取今日日期
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        
        print(f"检查日期: {today_str}")
        print("=" * 50)
        
        # 检查lottery_data集合
        lottery_collection = db['lottery_data']
        
        # 查询今日数据
        today_query = {'draw_date': {'$regex': f'^{today_str}'}}
        today_count = lottery_collection.count_documents(today_query)
        
        print(f"lottery_data集合中今日数据条数: {today_count}")
        
        if today_count > 0:
            # 显示最新几条数据
            latest_data = lottery_collection.find(today_query).sort([('scraped_at', -1)]).limit(5)
            print("\n最新5条今日数据:")
            for i, doc in enumerate(latest_data, 1):
                print(f"{i}. 期号: {doc.get('period', 'N/A')}, 开奖号码: {doc.get('draw_numbers', [])}, 开奖时间: {doc.get('draw_time', 'N/A')}, 有效性: {doc.get('is_valid', False)}")
        
        # 检查web_formatted_data集合
        web_collection = db['web_formatted_data']
        web_count = web_collection.count_documents({})
        
        print(f"\nweb_formatted_data集合总数据条数: {web_count}")
        
        if web_count > 0:
            # 显示最新的web格式化数据
            latest_web = web_collection.find().sort([('created_at', -1)]).limit(1)
            for doc in latest_web:
                data_count = len(doc.get('data', [])) if 'data' in doc else 0
                print(f"最新web格式化数据包含 {data_count} 条记录")
                print(f"创建时间: {doc.get('created_at', 'N/A')}")
                if data_count > 0:
                    print("前3条数据示例:")
                    for i, item in enumerate(doc['data'][:3], 1):
                        print(f"  {i}. {item}")
        
        # 检查所有数据的日期范围
        print("\n=" * 50)
        print("数据库中所有数据的日期范围:")
        
        # 获取最早和最晚的数据
        earliest = lottery_collection.find().sort([('scraped_at', 1)]).limit(1)
        latest = lottery_collection.find().sort([('scraped_at', -1)]).limit(1)
        
        for doc in earliest:
            print(f"最早数据: {doc.get('draw_date', 'N/A')} {doc.get('draw_time', 'N/A')}")
            
        for doc in latest:
            print(f"最新数据: {doc.get('draw_date', 'N/A')} {doc.get('draw_time', 'N/A')}")
        
        # 统计各日期的数据量
        pipeline = [
            {'$group': {
                '_id': '$draw_date',
                'count': {'$sum': 1},
                'valid_count': {'$sum': {'$cond': [{'$eq': ['$is_valid', True]}, 1, 0]}}
            }},
            {'$sort': {'_id': -1}},
            {'$limit': 10}
        ]
        
        print("\n最近10天的数据统计:")
        for result in lottery_collection.aggregate(pipeline):
            date = result['_id']
            total = result['count']
            valid = result['valid_count']
            print(f"{date}: 总计 {total} 条, 有效 {valid} 条")
        
        client.close()
        
    except Exception as e:
        print(f"检查数据时发生错误: {str(e)}")

if __name__ == '__main__':
    check_today_data()