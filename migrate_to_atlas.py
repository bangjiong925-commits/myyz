#!/usr/bin/env python3
"""
将数据从本地或Railway的MongoDB迁移到MongoDB Atlas的脚本

使用方法:
1. 设置源MongoDB和目标MongoDB Atlas的连接信息
2. 运行脚本: python migrate_to_atlas.py
"""

import os
import pymongo
import time
from datetime import datetime

# 源MongoDB连接信息 (本地或Railway)
SOURCE_MONGODB_URI = os.environ.get('SOURCE_MONGODB_URI', 'mongodb://localhost:27017/')
SOURCE_DB_NAME = os.environ.get('SOURCE_DB_NAME', 'taiwan_pk10')

# 目标MongoDB Atlas连接信息
TARGET_MONGODB_URI = os.environ.get('TARGET_MONGODB_URI', '')
TARGET_DB_NAME = os.environ.get('TARGET_DB_NAME', 'taiwan_pk10')

# 要迁移的集合列表
COLLECTIONS = ['data', 'lottery_data', 'web_formatted_data']

def connect_mongodb(uri, db_name, description):
    """连接到MongoDB数据库"""
    print(f'正在连接{description}数据库...')
    # 隐藏连接字符串中的敏感信息
    display_uri = uri.replace("://", "://*****:*****@") if "@" in uri else uri
    print(f'使用连接字符串: {display_uri}')
    print(f'数据库名称: {db_name}')
    
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        # 测试连接
        client.admin.command('ping')
        print(f'{description}数据库连接成功！')
        db = client[db_name]
        return client, db
    except Exception as e:
        print(f'连接{description}数据库失败: {e}')
        return None, None

def migrate_collection(source_db, target_db, collection_name):
    """迁移单个集合的数据"""
    print(f'\n开始迁移集合 {collection_name}...')
    
    # 检查源集合是否存在
    if collection_name not in source_db.list_collection_names():
        print(f'源数据库中不存在集合 {collection_name}，跳过迁移')
        return 0
    
    source_collection = source_db[collection_name]
    target_collection = target_db[collection_name]
    
    # 获取源集合中的文档数量
    total_docs = source_collection.count_documents({})
    print(f'源集合中共有 {total_docs} 条数据')
    
    if total_docs == 0:
        print(f'源集合 {collection_name} 中没有数据，跳过迁移')
        return 0
    
    # 检查目标集合中是否已有数据
    existing_docs = target_collection.count_documents({})
    if existing_docs > 0:
        print(f'警告: 目标集合 {collection_name} 中已有 {existing_docs} 条数据')
        confirm = input(f'是否继续迁移并添加到现有数据中？(y/n): ')
        if confirm.lower() != 'y':
            print(f'跳过迁移集合 {collection_name}')
            return 0
    
    # 批量迁移数据，每批1000条
    batch_size = 1000
    migrated_count = 0
    start_time = time.time()
    
    for i in range(0, total_docs, batch_size):
        batch = list(source_collection.find().skip(i).limit(batch_size))
        if batch:
            # 移除MongoDB的_id字段，让目标数据库自动生成新的_id
            for doc in batch:
                if '_id' in doc:
                    del doc['_id']
            
            # 插入到目标集合
            target_collection.insert_many(batch)
            migrated_count += len(batch)
            
            # 显示进度
            progress = min(migrated_count / total_docs * 100, 100)
            elapsed = time.time() - start_time
            print(f'进度: {progress:.1f}% ({migrated_count}/{total_docs}), 耗时: {elapsed:.1f}秒')
    
    print(f'集合 {collection_name} 迁移完成，共迁移 {migrated_count} 条数据')
    return migrated_count

def main():
    """主函数"""
    print('===== MongoDB数据迁移工具 =====')
    print(f'开始时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    
    # 检查目标MongoDB Atlas连接字符串是否设置
    if not TARGET_MONGODB_URI:
        print('错误: 未设置目标MongoDB Atlas连接字符串')
        print('请设置环境变量TARGET_MONGODB_URI，例如:')
        print('export TARGET_MONGODB_URI="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"')
        return
    
    # 连接源数据库
    source_client, source_db = connect_mongodb(SOURCE_MONGODB_URI, SOURCE_DB_NAME, '源')
    if not source_client or not source_db:
        return
    
    # 连接目标数据库
    target_client, target_db = connect_mongodb(TARGET_MONGODB_URI, TARGET_DB_NAME, '目标')
    if not target_client or not target_db:
        source_client.close()
        return
    
    try:
        # 迁移每个集合
        total_migrated = 0
        for collection_name in COLLECTIONS:
            migrated = migrate_collection(source_db, target_db, collection_name)
            total_migrated += migrated
        
        print(f'\n===== 迁移完成 =====')
        print(f'总共迁移 {total_migrated} 条数据')
        print(f'结束时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
    except Exception as e:
        print(f'迁移过程中出错: {e}')
    finally:
        # 关闭数据库连接
        source_client.close()
        target_client.close()

if __name__ == '__main__':
    main()