#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from datetime import datetime
from urllib.parse import quote_plus

def view_today_data():
    """查看云端数据库中今天的数据"""
    
    # 直接使用连接字符串
    username = "zhu"
    password = "83OmNawYN85nI98i"
    cluster = "cluster0.p4yg8ug.mongodb.net"
    database = "taiwan_pk10"
    
    # URL编码用户名和密码
    encoded_username = quote_plus(username)
    encoded_password = quote_plus(password)
    
    # 构建连接字符串
    mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster}/{database}?retryWrites=true&w=majority"
    
    print("正在连接到MongoDB Atlas云端数据库...")
    print(f"集群地址: {cluster}")
    print(f"数据库: {database}")
    print("=" * 60)
    
    try:
        # 连接到MongoDB
        client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ 云端数据库连接成功！")
        
        # 获取数据库
        db = client[database]
        
        # 获取今日日期
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        
        print(f"\n📅 查询日期: {today_str}")
        print("=" * 60)
        
        # 列出所有集合
        collections = db.list_collection_names()
        print(f"📊 数据库中的集合: {collections}")
        
        # 检查lottery_data集合
        if 'lottery_data' in collections:
            lottery_collection = db['lottery_data']
            
            # 查询今日数据
            today_query = {'draw_date': {'$regex': f'^{today_str}'}}
            today_count = lottery_collection.count_documents(today_query)
            
            print(f"\n🎲 lottery_data集合中今日数据条数: {today_count}")
            
            if today_count > 0:
                print("\n📋 最新5条今日数据:")
                print("-" * 80)
                latest_data = lottery_collection.find(today_query).sort([('scraped_at', -1)]).limit(5)
                for i, doc in enumerate(latest_data, 1):
                    period = doc.get('period', 'N/A')
                    numbers = doc.get('draw_numbers', [])
                    draw_time = doc.get('draw_time', 'N/A')
                    is_valid = doc.get('is_valid', False)
                    status = "✅ 有效" if is_valid else "❌ 无效"
                    print(f"{i:2d}. 期号: {period:>8} | 开奖号码: {str(numbers):>20} | 时间: {draw_time:>8} | {status}")
            else:
                print(f"\n⚠️  今天({today_str})暂无数据")
        else:
            print("\n❌ lottery_data集合不存在")
        
        # 检查web_formatted_data集合
        if 'web_formatted_data' in collections:
            web_collection = db['web_formatted_data']
            web_count = web_collection.count_documents({})
            
            print(f"\n🌐 web_formatted_data集合总数据条数: {web_count}")
            
            if web_count > 0:
                # 显示最新的web格式化数据
                latest_web = web_collection.find().sort([('created_at', -1)]).limit(1)
                for doc in latest_web:
                    data_count = len(doc.get('data', [])) if 'data' in doc else 0
                    created_at = doc.get('created_at', 'N/A')
                    print(f"📦 最新web格式化数据包含 {data_count} 条记录")
                    print(f"🕒 创建时间: {created_at}")
                    
                    if data_count > 0:
                        print("\n📝 前3条数据示例:")
                        for i, item in enumerate(doc['data'][:3], 1):
                            print(f"   {i}. {item}")
        
        # 统计各日期的数据量
        if 'lottery_data' in collections:
            print("\n" + "=" * 60)
            print("📈 最近10天的数据统计:")
            print("-" * 60)
            
            pipeline = [
                {'$group': {
                    '_id': '$draw_date',
                    'count': {'$sum': 1},
                    'valid_count': {'$sum': {'$cond': [{'$eq': ['$is_valid', True]}, 1, 0]}}
                }},
                {'$sort': {'_id': -1}},
                {'$limit': 10}
            ]
            
            for result in lottery_collection.aggregate(pipeline):
                date = result['_id']
                total = result['count']
                valid = result['valid_count']
                print(f"📅 {date}: 总计 {total:>3} 条, 有效 {valid:>3} 条")
        
        print("\n" + "=" * 60)
        print("✅ 云端数据库查询完成！")
        
        client.close()
        
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f"❌ 无法连接到MongoDB Atlas服务器: {e}")
        print("\n可能的原因:")
        print("1. 网络连接问题")
        print("2. IP地址未添加到MongoDB Atlas的访问列表中")
    except pymongo.errors.OperationFailure as e:
        print(f"❌ 认证失败: {e}")
        print("\n可能的原因:")
        print("1. 用户名或密码不正确")
        print("2. 用户没有足够的权限")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == '__main__':
    view_today_data()