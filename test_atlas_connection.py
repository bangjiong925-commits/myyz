#!/usr/bin/env python3
"""
测试MongoDB Atlas连接的脚本

使用方法:
1. 设置环境变量MONGODB_URI和MONGODB_DB_NAME
2. 运行脚本: python test_atlas_connection.py
"""

import os
import pymongo
import sys
from datetime import datetime

def main():
    """测试MongoDB Atlas连接"""
    print('===== MongoDB Atlas连接测试 =====')
    print(f'开始时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    
    # 获取MongoDB连接信息
    mongodb_uri = os.environ.get('MONGODB_URI')
    db_name = os.environ.get('MONGODB_DB_NAME', 'taiwan_pk10')
    
    if not mongodb_uri:
        print('错误: 未设置MONGODB_URI环境变量')
        print('请设置环境变量，例如:')
        print('export MONGODB_URI="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"')
        sys.exit(1)
    
    # 隐藏连接字符串中的敏感信息
    display_uri = mongodb_uri.replace("://", "://*****:*****@") if "@" in mongodb_uri else mongodb_uri
    print(f'使用连接字符串: {display_uri}')
    print(f'数据库名称: {db_name}')
    
    try:
        # 连接到MongoDB
        print('正在连接到MongoDB Atlas...')
        client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # 测试连接
        client.admin.command('ping')
        print('MongoDB Atlas连接成功！')
        
        # 获取数据库
        db = client[db_name]
        
        # 列出所有集合
        collections = db.list_collection_names()
        print(f'\n数据库中的集合: {collections}')
        
        # 检查关键集合
        key_collections = ['data', 'lottery_data', 'web_formatted_data']
        for collection_name in key_collections:
            if collection_name in collections:
                count = db[collection_name].count_documents({})
                print(f'集合 {collection_name} 中有 {count} 条数据')
            else:
                print(f'集合 {collection_name} 不存在')
        
        # 如果lottery_data集合存在，获取最新的一条数据
        if 'lottery_data' in collections:
            latest_doc = db['lottery_data'].find_one(sort=[('date', pymongo.DESCENDING)])
            if latest_doc:
                print(f'\n最新的lottery_data数据:')
                print(f'日期: {latest_doc.get("date")}')
                print(f'期号: {latest_doc.get("issue")}')
                print(f'开奖号码: {latest_doc.get("numbers")}')
        
        print('\n===== 连接测试完成 =====')
        print('MongoDB Atlas连接和数据验证成功！')
        
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f'\n错误: 无法连接到MongoDB Atlas服务器: {e}')
        print('\n可能的原因:')
        print('1. 连接字符串不正确')
        print('2. 网络连接问题')
        print('3. IP地址未添加到MongoDB Atlas的IP访问列表中')
        print('\n解决方案:')
        print('1. 检查连接字符串是否正确')
        print('2. 检查网络连接')
        print('3. 在MongoDB Atlas控制台中添加您的IP地址到访问列表')
        sys.exit(1)
    except pymongo.errors.OperationFailure as e:
        print(f'\n错误: 操作失败: {e}')
        print('\n可能的原因:')
        print('1. 用户名或密码不正确')
        print('2. 用户没有足够的权限')
        print('\n解决方案:')
        print('1. 检查用户名和密码')
        print('2. 确保用户有适当的权限')
        sys.exit(1)
    except Exception as e:
        print(f'\n错误: {e}')
        sys.exit(1)
    finally:
        # 关闭连接
        if 'client' in locals():
            client.close()

if __name__ == '__main__':
    main()