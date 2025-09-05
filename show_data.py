#!/usr/bin/env python3
import os
from pymongo import MongoClient
from datetime import datetime

# 从环境变量获取MongoDB连接信息
mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
collection_name = 'lottery_data'

try:
    # 连接MongoDB
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    # 获取数据统计信息
    total_count = collection.count_documents({})
    
    if total_count == 0:
        print("远程MongoDB数据库中暂无数据")
        exit(1)
    
    # 获取最新和最早的记录
    latest_record = collection.find().sort('issue_number', -1).limit(1)[0]
    earliest_record = collection.find().sort('issue_number', 1).limit(1)[0]
    
    print(f"远程MongoDB数据库统计信息:")
    print(f"总记录数: {total_count}")
    print(f"最新记录期号: {latest_record['issue_number']}")
    print(f"最早记录期号: {earliest_record['issue_number']}")
    print(f"最新开奖时间: {latest_record['draw_time']}")
    print(f"最早开奖时间: {earliest_record['draw_time']}")
    print(f"数据源: {latest_record.get('data_source', 'N/A')}")
    print()
    
    # 获取最新5条记录
    print("最新5条开奖记录:")
    latest_records = collection.find().sort('issue_number', -1).limit(5)
    for record in latest_records:
        print(f"期号: {record['issue_number']}, 开奖号码: {record['draw_numbers']}, 时间: {record['draw_time']}")
    
    print()
    
    # 获取最早5条记录
    print("最早5条开奖记录:")
    earliest_records = collection.find().sort('issue_number', 1).limit(5)
    for record in earliest_records:
        print(f"期号: {record['issue_number']}, 开奖号码: {record['draw_numbers']}, 时间: {record['draw_time']}")
    
    client.close()
    
except Exception as e:
    print(f"连接远程MongoDB数据库失败: {e}")
    print("请确保MONGODB_URI环境变量已正确设置")
    exit(1)