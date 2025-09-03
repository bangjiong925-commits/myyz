#!/usr/bin/env python3
import pymongo
from datetime import datetime

try:
    # 连接MongoDB数据库
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['taiwan_pk10']
    
    # 检查所有集合
    collections = db.list_collection_names()
    print(f'数据库中的集合: {collections}')
    
    # 检查两个可能的集合
    data_collection = db['data']
    lottery_collection = db['lottery_data']
    
    # 获取今天的日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查data集合
    data_count = data_collection.count_documents({'date': today})
    print(f'\ndata集合 - 今天({today})共有 {data_count} 条数据')
    
    # 检查lottery_data集合
    lottery_count = lottery_collection.count_documents({'draw_date': today})
    print(f'lottery_data集合 - 今天({today})共有 {lottery_count} 条数据')
    
    # 获取lottery_data集合的最近5条数据
    recent_lottery_data = list(lottery_collection.find({'draw_date': today}).sort('_id', -1).limit(5))
    
    if recent_lottery_data:
        print('\nlottery_data集合最近5条数据:')
        for i, data in enumerate(recent_lottery_data, 1):
            period = data.get('period', 'N/A')
            numbers = data.get('draw_numbers', 'N/A')
            time = data.get('draw_time', 'N/A')
            print(f'{i}. 期号: {period}, 开奖号码: {numbers}, 时间: {time}')
    else:
        print('\nlottery_data集合今天暂无数据')
        
    # 获取数据库总数据量
    data_total = data_collection.count_documents({})
    lottery_total = lottery_collection.count_documents({})
    print(f'\ndata集合总共有 {data_total} 条数据')
    print(f'lottery_data集合总共有 {lottery_total} 条数据')
    
    # 获取lottery_data集合中所有日期的统计
    pipeline = [
        {'$group': {'_id': '$draw_date', 'count': {'$sum': 1}}},
        {'$sort': {'_id': -1}}
    ]
    lottery_date_stats = list(lottery_collection.aggregate(pipeline))
    
    if lottery_date_stats:
        print('\nlottery_data集合各日期数据统计:')
        for stat in lottery_date_stats[:10]:  # 显示最近10天
            print(f'{stat["_id"]}: {stat["count"]} 条数据')
    
    # 检查lottery_data集合最新的几条数据（不限日期）
    latest_lottery = list(lottery_collection.find().sort('_id', -1).limit(5))
    if latest_lottery:
        print('\nlottery_data集合中最新的5条数据（不限日期）:')
        for i, data in enumerate(latest_lottery, 1):
            period = data.get('period', 'N/A')
            numbers = data.get('draw_numbers', 'N/A')
            time = data.get('draw_time', 'N/A')
            date = data.get('draw_date', 'N/A')
            print(f'{i}. 日期: {date}, 期号: {period}, 开奖号码: {numbers}, 时间: {time}')
    
except Exception as e:
    print(f'查询数据库时出错: {e}')
finally:
    if 'client' in locals():
        client.close()