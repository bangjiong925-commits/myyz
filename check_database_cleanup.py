#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库清理检查脚本
检查数据库中的数据量和清理策略
"""

import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from collections import defaultdict

def connect_to_mongodb():
    """连接到MongoDB数据库"""
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    mongodb_db_name = os.getenv('MONGODB_DB_NAME', 'taiwan_pk10')
    
    print(f"正在连接数据库...")
    print(f"使用连接字符串: {mongodb_uri}")
    print(f"数据库名称: {mongodb_db_name}")
    
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # 测试连接
        db = client[mongodb_db_name]
        print("数据库连接成功！")
        return client, db
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None, None

def analyze_data_distribution(db):
    """分析数据分布情况"""
    print("\n=== 数据分布分析 ===")
    
    collections = ['lottery_data', 'web_formatted_data', 'taiwanPK10Data']
    
    for collection_name in collections:
        if collection_name in db.list_collection_names():
            collection = db[collection_name]
            total_count = collection.count_documents({})
            print(f"\n{collection_name} 集合:")
            print(f"  总数据量: {total_count} 条")
            
            if total_count > 0:
                # 按日期统计数据
                pipeline = [
                    {
                        "$group": {
                            "_id": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d",
                                    "date": "$date"
                                }
                            },
                            "count": {"$sum": 1}
                        }
                    },
                    {"$sort": {"_id": -1}},
                    {"$limit": 10}
                ]
                
                try:
                    date_stats = list(collection.aggregate(pipeline))
                    if date_stats:
                        print("  最近10天数据分布:")
                        for stat in date_stats:
                            print(f"    {stat['_id']}: {stat['count']} 条")
                    
                    # 检查最老的数据
                    oldest = collection.find().sort("date", 1).limit(1)
                    newest = collection.find().sort("date", -1).limit(1)
                    
                    oldest_doc = list(oldest)
                    newest_doc = list(newest)
                    
                    if oldest_doc and newest_doc:
                        oldest_date = oldest_doc[0].get('date')
                        newest_date = newest_doc[0].get('date')
                        
                        if oldest_date and newest_date:
                            print(f"  数据时间范围: {oldest_date} 到 {newest_date}")
                            
                            # 计算数据跨度
                            if isinstance(oldest_date, datetime) and isinstance(newest_date, datetime):
                                span_days = (newest_date - oldest_date).days
                                print(f"  数据跨度: {span_days} 天")
                                
                                # 检查是否有超过30天的旧数据
                                thirty_days_ago = datetime.now() - timedelta(days=30)
                                old_data_count = collection.count_documents({
                                    "date": {"$lt": thirty_days_ago}
                                })
                                
                                if old_data_count > 0:
                                    print(f"  ⚠️  超过30天的旧数据: {old_data_count} 条")
                                    print(f"     建议清理 {thirty_days_ago.strftime('%Y-%m-%d')} 之前的数据")
                                else:
                                    print("  ✅ 无需清理旧数据")
                                    
                except Exception as e:
                    print(f"  分析数据分布时出错: {e}")

def check_disk_usage():
    """检查磁盘使用情况"""
    print("\n=== 磁盘使用情况 ===")
    try:
        import shutil
        total, used, free = shutil.disk_usage("/Users/a1234/Documents/GitHub/myyz")
        
        print(f"总空间: {total // (1024**3)} GB")
        print(f"已使用: {used // (1024**3)} GB")
        print(f"可用空间: {free // (1024**3)} GB")
        print(f"使用率: {(used/total)*100:.1f}%")
        
        if (used/total) > 0.8:
            print("⚠️  磁盘使用率超过80%，建议清理数据")
        else:
            print("✅ 磁盘空间充足")
            
    except Exception as e:
        print(f"检查磁盘使用情况时出错: {e}")

def generate_cleanup_recommendations(db):
    """生成清理建议"""
    print("\n=== 清理建议 ===")
    
    recommendations = []
    
    # 检查各集合的数据量
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        count = collection.count_documents({})
        
        if count > 10000:
            recommendations.append(f"• {collection_name} 集合有 {count} 条数据，考虑清理旧数据")
        
        # 检查30天前的数据
        thirty_days_ago = datetime.now() - timedelta(days=30)
        old_count = collection.count_documents({
            "date": {"$lt": thirty_days_ago}
        })
        
        if old_count > 0:
            recommendations.append(f"• {collection_name} 集合有 {old_count} 条超过30天的数据可以清理")
    
    if recommendations:
        print("建议执行以下清理操作:")
        for rec in recommendations:
            print(rec)
    else:
        print("✅ 当前数据库状态良好，无需特殊清理")
    
    # 生成清理脚本建议
    print("\n如需清理数据，可以使用以下MongoDB命令:")
    print("# 删除30天前的数据")
    thirty_days_ago = datetime.now() - timedelta(days=30)
    print(f'db.lottery_data.deleteMany({{"date": {{"$lt": ISODate("{thirty_days_ago.isoformat()}")}}}});')
    print(f'db.web_formatted_data.deleteMany({{"date": {{"$lt": ISODate("{thirty_days_ago.isoformat()}")}}}});')

def main():
    """主函数"""
    print("数据库清理检查工具")
    print("=" * 50)
    
    client, db = connect_to_mongodb()
    if client is None or db is None:
        return
    
    try:
        # 分析数据分布
        analyze_data_distribution(db)
        
        # 检查磁盘使用情况
        check_disk_usage()
        
        # 生成清理建议
        generate_cleanup_recommendations(db)
        
    except Exception as e:
        print(f"检查过程中出现错误: {e}")
    finally:
        client.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()