#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试今日数据查询
"""

import os
import sys
from datetime import datetime
try:
    import pymongo
except ImportError:
    print("错误: 需要安装pymongo库")
    print("请运行: pip install pymongo")
    sys.exit(1)

def test_mongodb_connection():
    """测试MongoDB连接"""
    # 从环境变量获取连接字符串
    mongodb_uri = "mongodb+srv://a1234:Aa123456@cluster0.aqhqe.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"
    
    try:
        print("正在连接MongoDB Atlas...")
        client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB连接成功")
        
        # 获取数据库
        db = client.taiwan_pk10
        print(f"数据库: {db.name}")
        
        # 获取集合列表
        collections = db.list_collection_names()
        print(f"集合: {collections}")
        
        if 'taiwan_pk10_data' in collections:
            collection = db.taiwan_pk10_data
            
            # 统计总数据条数
            total_count = collection.count_documents({})
            print(f"总数据条数: {total_count}")
            
            # 查询今日数据
            today = '2025-09-04'
            today_count = collection.count_documents({'date': today})
            print(f"今日({today})数据条数: {today_count}")
            
            if today_count > 0:
                # 获取最新的几条记录
                latest_records = list(collection.find({'date': today}).sort('period', -1).limit(3))
                print(f"\n最新3条记录:")
                for i, record in enumerate(latest_records, 1):
                    print(f"  {i}. 期号: {record.get('period', 'N/A')}, 时间: {record.get('time', 'N/A')}")
                    print(f"     开奖号码: {record.get('numbers', 'N/A')}")
                    print(f"     记录时间: {record.get('timestamp', 'N/A')}")
                    print()
            else:
                print(f"今日({today})暂无数据")
                
                # 查看最近的数据
                recent_records = list(collection.find().sort('timestamp', -1).limit(3))
                if recent_records:
                    print("\n最近的3条数据:")
                    for i, record in enumerate(recent_records, 1):
                        print(f"  {i}. 日期: {record.get('date', 'N/A')}, 期号: {record.get('period', 'N/A')}")
                        print(f"     开奖号码: {record.get('numbers', 'N/A')}")
                        print(f"     记录时间: {record.get('timestamp', 'N/A')}")
                        print()
        else:
            print("❌ taiwan_pk10_data集合不存在")
            print("可用集合:", collections)
            
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f"❌ 连接超时: {e}")
        print("可能的原因:")
        print("1. 网络连接问题")
        print("2. MongoDB Atlas集群未启动")
        print("3. 连接字符串错误")
        print("4. IP白名单限制")
    except pymongo.errors.ConfigurationError as e:
        print(f"❌ 配置错误: {e}")
        print("请检查连接字符串格式")
    except pymongo.errors.AuthenticationFailed as e:
        print(f"❌ 认证失败: {e}")
        print("请检查用户名和密码")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")

if __name__ == "__main__":
    print("台湾PK10数据查询测试")
    print("=" * 40)
    print(f"查询日期: 2025-09-04")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_mongodb_connection()