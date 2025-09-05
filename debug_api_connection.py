#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import os
from datetime import datetime, timezone, timedelta

print('=== API服务器连接调试 ===')

# 模拟API服务器的连接逻辑
class APIHandler:
    def __init__(self):
        # 完全复制API服务器的连接逻辑
        self.mongo_uri = os.environ.get('MONGODB_URI', 'mongodb+srv://a1234:a1234@cluster0.mongodb.net/')
        self.db_name = 'taiwan_pk10'
        self.collection_name = 'lottery_data'
        print(f'使用的URI: {self.mongo_uri}')
    
    def test_connection(self):
        try:
            print('\n尝试连接MongoDB...')
            client = MongoClient(self.mongo_uri)
            print('MongoClient创建成功')
            
            # 测试连接
            db = client[self.db_name]
            collection = db[self.collection_name]
            print('数据库和集合访问成功')
            
            # 尝试查询
            count = collection.count_documents({})
            print(f'查询成功，总记录数: {count}')
            
            # 获取最新记录
            latest = list(collection.find().sort('period', -1).limit(1))
            if latest:
                print(f'最新记录期号: {latest[0]["period"]}')
            
            client.close()
            return True, count
            
        except Exception as e:
            print(f'连接失败: {e}')
            print(f'错误类型: {type(e).__name__}')
            return False, str(e)

# 测试
api = APIHandler()
success, result = api.test_connection()

if not success:
    print('\n=== 分析 ===')
    print('API服务器的云端连接确实失败了')
    print('但API仍然返回数据，说明存在其他数据源或回退机制')
    
    # 检查是否有其他可能的连接方式
    print('\n检查可能的本地回退...')
    try:
        local_client = MongoClient('mongodb://localhost:27017/')
        local_db = local_client['taiwan_pk10']
        local_count = local_db['lottery_data'].count_documents({})
        print(f'本地数据库确实存在，记录数: {local_count}')
        local_client.close()
    except Exception as e:
        print(f'本地数据库也不可用: {e}')
else:
    print(f'\n=== 结论 ===\n云端连接成功，数据来自云端MongoDB Atlas，记录数: {result}')