#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import os

print('=== 数据库连接测试 ===')

# 测试API服务器使用的连接字符串
api_uri = os.environ.get('MONGODB_URI', 'mongodb+srv://a1234:a1234@cluster0.mongodb.net/')
print(f'API服务器URI: {api_uri}')

try:
    print('\n1. 测试云端MongoDB Atlas连接...')
    client = MongoClient(api_uri, serverSelectionTimeoutMS=5000)
    client.server_info()
    print('✓ 云端连接: 成功')
    db = client['taiwan_pk10']
    count = db['lottery_data'].count_documents({})
    print(f'✓ 云端数据条数: {count}')
    latest = list(db['lottery_data'].find().sort('period', -1).limit(1))
    if latest:
        print(f'✓ 云端最新期号: {latest[0]["period"]}')
    client.close()
except Exception as e:
    print(f'✗ 云端连接失败: {e}')
    
    print('\n2. 测试本地MongoDB连接...')
    try:
        local_client = MongoClient('mongodb://localhost:27017/')
        local_client.server_info()
        print('✓ 本地连接: 成功')
        local_db = local_client['taiwan_pk10']
        local_count = local_db['lottery_data'].count_documents({})
        print(f'✓ 本地数据条数: {local_count}')
        local_latest = list(local_db['lottery_data'].find().sort('period', -1).limit(1))
        if local_latest:
            print(f'✓ 本地最新期号: {local_latest[0]["period"]}')
        local_client.close()
        
        print('\n=== 结论 ===')
        print('API服务器实际使用的是本地MongoDB数据库')
    except Exception as e2:
        print(f'✗ 本地连接也失败: {e2}')
        print('\n=== 结论 ===')
        print('无法确定数据来源')