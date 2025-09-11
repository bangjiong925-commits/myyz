#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步数据到MongoDB Atlas
创建今日数据和历史数据
"""

import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def sync_data_to_atlas():
    """同步数据到MongoDB Atlas"""
    try:
        # 获取连接信息
        mongo_uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
        
        if not mongo_uri:
            print("❌ 未找到MONGODB_URI环境变量")
            return False
        
        print(f"连接到MongoDB Atlas: {mongo_uri[:50]}...")
        
        # 连接数据库
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB Atlas连接成功！")
        
        # 创建今日数据
        today = datetime.now().strftime('%Y-%m-%d')
        today_collection = db['today_data']
        
        today_data = {
            'date': today,
            'last_updated': datetime.now().isoformat(),
            'periods': [
                {
                    'period': f'{today.replace("-", "")}01',
                    'time': '09:10',
                    'numbers': [3, 7, 1, 9, 5, 2, 8, 4, 6, 10],
                    'draw_time': f'{today} 09:10:00'
                },
                {
                    'period': f'{today.replace("-", "")}02',
                    'time': '09:30',
                    'numbers': [8, 2, 5, 1, 9, 7, 3, 6, 4, 10],
                    'draw_time': f'{today} 09:30:00'
                },
                {
                    'period': f'{today.replace("-", "")}03',
                    'time': '09:50',
                    'numbers': [5, 9, 3, 7, 1, 6, 2, 8, 4, 10],
                    'draw_time': f'{today} 09:50:00'
                }
            ]
        }
        
        # 插入今日数据
        result = today_collection.replace_one(
            {'date': today},
            today_data,
            upsert=True
        )
        
        if result.upserted_id or result.modified_count > 0:
            print(f"✅ 今日数据已同步 ({len(today_data['periods'])} 期)")
        else:
            print("ℹ️  今日数据无变化")
        
        # 创建历史数据
        history_collection = db['taiwan_pk10_data']
        
        # 生成最近3天的历史数据
        history_data = []
        for i in range(1, 4):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            date_str = date.replace('-', '')
            
            periods = []
            for j in range(1, 4):  # 每天3期
                periods.append({
                    'period': f'{date_str}{j:02d}',
                    'time': f'{8 + j}:{10 + j*20:02d}',
                    'numbers': [(j*2 + k) % 10 + 1 for k in range(10)],
                    'draw_time': f'{date} {8 + j}:{10 + j*20:02