#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库清理脚本 - 删除历史数据，只保留指定日期的数据
"""

import os
import sys
import argparse
from datetime import datetime, date, timedelta

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("错误: pymongo未安装，无法连接MongoDB")
    print("请运行: pip install pymongo")
    sys.exit(1)

def cleanup_by_period_range(mongodb_uri="mongodb://localhost:27017", db_name="taiwan_pk10", start_period=None, end_period=None):
    """
    清理数据库，只保留指定期号范围的数据
    
    Args:
        mongodb_uri: MongoDB连接URI
        db_name: 数据库名称
        start_period: 起始期号（字符串或整数）
        end_period: 结束期号（字符串或整数）
    """
    if not start_period or not end_period:
        print("错误: 必须指定起始期号和结束期号")
        return False
    
    # 转换期号为字符串（因为数据库中期号存储为字符串）
    start_period_str = str(start_period)
    end_period_str = str(end_period)
    
    print(f"开始清理数据库: {db_name}")
    print(f"MongoDB URI: {mongodb_uri}")
    print(f"保留期号范围: {start_period_str} - {end_period_str}")
    print("-" * 50)
    
    try:
        # 连接MongoDB
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        # 测试连接
        client.admin.command('ping')
        print("✓ MongoDB连接成功")
        
        # 清理lottery_data集合
        print("\n正在清理 lottery_data 集合...")
        lottery_collection = db['lottery_data']
        
        # 统计清理前的数据
        total_before_lottery = lottery_collection.count_documents({})
        target_before_lottery = lottery_collection.count_documents({
            'period': {'$gte': start_period_str, '$lte': end_period_str}
        })
        
        print(f"清理前总记录数: {total_before_lottery}")
        print(f"目标期号范围记录数: {target_before_lottery}")
        
        # 删除不在期号范围内的数据
        delete_result_lottery = lottery_collection.delete_many({
            '$or': [
                {'period': {'$lt': start_period_str}},
                {'period': {'$gt': end_period_str}}
            ]
        })
        
        print(f"删除记录数: {delete_result_lottery.deleted_count}")
        
        # 清理web_formatted_data集合 - 删除所有数据，因为这些是格式化缓存
        print("\n正在清理 web_formatted_data 集合...")
        web_collection = db['web_formatted_data']
        
        total_before_web = web_collection.count_documents({})
        delete_result_web = web_collection.delete_many({})
        
        print(f"清理前总记录数: {total_before_web}")
        print(f"删除记录数: {delete_result_web.deleted_count}")
        
        # 统计清理后的数据
        remaining_lottery = lottery_collection.count_documents({})
        remaining_web = web_collection.count_documents({})
        
        print("\n" + "=" * 50)
        print("清理完成！")
        print(f"lottery_data 集合: 删除 {delete_result_lottery.deleted_count} 条，剩余 {remaining_lottery} 条")
        print(f"web_formatted_data 集合: 删除 {delete_result_web.deleted_count} 条，剩余 {remaining_web} 条")
        print(f"总计: 删除 {delete_result_lottery.deleted_count + delete_result_web.deleted_count} 条，剩余 {remaining_lottery + remaining_web} 条")
        print(f"保留期号范围: {start_period_str} - {end_period_str}")
        print(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ 清理失败: {e}")
        return False

def cleanup_by_days(mongodb_uri="mongodb://localhost:27017", db_name="taiwan_pk10", keep_days=7):
    """
    清理数据库，只保留最近指定天数的数据
    
    Args:
        mongodb_uri: MongoDB连接URI
        db_name: 数据库名称
        keep_days: 保留的天数（默认7天）
    """
    # 计算保留数据的起始日期
    cutoff_date = (date.today() - timedelta(days=keep_days-1)).isoformat()
    
    print(f"开始清理数据库: {db_name}")
    print(f"MongoDB URI: {mongodb_uri}")
    print(f"保留最近 {keep_days} 天的数据")
    print(f"保留数据起始日期: {cutoff_date}")
    print("-" * 50)
    
    try:
        # 连接MongoDB
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        # 测试连接
        client.admin.command('ping')
        print("✓ MongoDB连接成功")
        
        # 清理lottery_data集合
        print("\n正在清理 lottery_data 集合...")
        lottery_collection = db['lottery_data']
        
        # 统计清理前的数据
        total_before_lottery = lottery_collection.count_documents({})
        
        # 删除超过保留天数的数据
        delete_result_lottery = lottery_collection.delete_many({
            'draw_date': {'$lt': cutoff_date}
        })
        
        print(f"清理前总记录数: {total_before_lottery}")
        print(f"删除记录数: {delete_result_lottery.deleted_count}")
        
        # 清理web_formatted_data集合
        print("\n正在清理 web_formatted_data 集合...")
        web_collection = db['web_formatted_data']
        
        # 统计清理前的数据
        total_before_web = web_collection.count_documents({})
        
        # 删除超过保留天数的数据
        delete_result_web = web_collection.delete_many({
            'created_at': {'$lt': cutoff_date}
        })
        
        print(f"清理前总记录数: {total_before_web}")
        print(f"删除记录数: {delete_result_web.deleted_count}")
        
        # 统计清理后的数据
        remaining_lottery = lottery_collection.count_documents({})
        remaining_web = web_collection.count_documents({})
        
        print("\n" + "=" * 50)
        print("清理完成！")
        print(f"lottery_data 集合: 删除 {delete_result_lottery.deleted_count} 条，剩余 {remaining_lottery} 条")
        print(f"web_formatted_data 集合: 删除 {delete_result_web.deleted_count} 条，剩余 {remaining_web} 条")
        print(f"总计: 删除 {delete_result_lottery.deleted_count + delete_result_web.deleted_count} 条，剩余 {remaining_lottery + remaining_web} 条")
        print(f"保留天数: {keep_days} 天")
        print(f"保留数据起始日期: {cutoff_date}")
        print(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ 清理失败: {e}")
        return False

def cleanup_database(mongodb_uri="mongodb://localhost:27017", db_name="taiwan_pk10", target_date=None):
    """
    清理数据库，只保留指定日期的数据
    
    Args:
        mongodb_uri: MongoDB连接URI
        db_name: 数据库名称
        target_date: 要保留的日期 (格式: YYYY-MM-DD)，默认为今天
    """
    if not target_date:
        target_date = date.today().isoformat()
    
    print(f"开始清理数据库: {db_name}")
    print(f"MongoDB URI: {mongodb_uri}")
    print(f"保留日期: {target_date}")
    print("-" * 50)
    
    try:
        # 连接MongoDB
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        # 测试连接
        client.admin.command('ping')
        print("✓ MongoDB连接成功")
        
        # 清理lottery_data集合
        print("\n正在清理 lottery_data 集合...")
        lottery_collection = db['lottery_data']
        
        # 统计清理前的数据
        total_before_lottery = lottery_collection.count_documents({})
        target_before_lottery = lottery_collection.count_documents({
            'draw_date': {'$regex': f'^{target_date}'}
        })
        
        print(f"清理前总记录数: {total_before_lottery}")
        print(f"目标日期记录数: {target_before_lottery}")
        
        # 删除不是目标日期的数据
        delete_result_lottery = lottery_collection.delete_many({
            'draw_date': {'$not': {'$regex': f'^{target_date}'}}
        })
        
        print(f"删除记录数: {delete_result_lottery.deleted_count}")
        
        # 清理web_formatted_data集合
        print("\n正在清理 web_formatted_data 集合...")
        web_collection = db['web_formatted_data']
        
        # 统计清理前的数据
        total_before_web = web_collection.count_documents({})
        target_before_web = web_collection.count_documents({
            'created_at': {'$regex': f'^{target_date}'}
        })
        
        print(f"清理前总记录数: {total_before_web}")
        print(f"目标日期记录数: {target_before_web}")
        
        # 删除不是目标日期创建的数据
        delete_result_web = web_collection.delete_many({
            'created_at': {'$not': {'$regex': f'^{target_date}'}}
        })
        
        print(f"删除记录数: {delete_result_web.deleted_count}")
        
        # 统计清理后的数据
        remaining_lottery = lottery_collection.count_documents({})
        remaining_web = web_collection.count_documents({})
        
        print("\n" + "=" * 50)
        print("清理完成！")
        print(f"lottery_data 集合: 删除 {delete_result_lottery.deleted_count} 条，剩余 {remaining_lottery} 条")
        print(f"web_formatted_data 集合: 删除 {delete_result_web.deleted_count} 条，剩余 {remaining_web} 条")
        print(f"总计: 删除 {delete_result_lottery.deleted_count + delete_result_web.deleted_count} 条，剩余 {remaining_lottery + remaining_web} 条")
        print(f"保留日期: {target_date}")
        print(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ 清理失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='数据库清理脚本')
    parser.add_argument('--mongodb-uri', default='mongodb://localhost:27017', 
                       help='MongoDB连接URI (默认: mongodb://localhost:27017)')
    parser.add_argument('--db-name', default='taiwan_pk10', 
                       help='数据库名称 (默认: taiwan_pk10)')
    parser.add_argument('--target-date', 
                       help='要保留的日期 (格式: YYYY-MM-DD，默认为今天)')
    parser.add_argument('--start-period', type=int,
                       help='起始期号 (与--end-period一起使用，按期号范围清理)')
    parser.add_argument('--end-period', type=int,
                       help='结束期号 (与--start-period一起使用，按期号范围清理)')
    parser.add_argument('--keep-days', type=int, default=7,
                       help='保留最近几天的数据 (默认: 7天)')
    parser.add_argument('--confirm', action='store_true', 
                       help='确认执行清理操作（不加此参数将只显示预览）')
    
    args = parser.parse_args()
    
    # 从环境变量获取配置
    mongodb_uri = args.mongodb_uri or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = args.db_name or os.environ.get('MONGODB_DB_NAME', 'taiwan_pk10')
    
    # 检查清理模式
    if args.start_period and args.end_period:
        # 按期号范围清理
        print("数据库清理脚本 - 按期号范围清理")
        print("=" * 50)
        print(f"MongoDB URI: {mongodb_uri}")
        print(f"数据库名称: {db_name}")
        print(f"保留期号范围: {args.start_period} - {args.end_period}")
        print(f"确认执行: {'是' if args.confirm else '否（预览模式）'}")
        
        if not args.confirm:
            print("\n⚠️  这是预览模式，不会实际删除数据")
            print("要执行实际清理，请添加 --confirm 参数")
            print("\n示例:")
            print(f"  python3 {sys.argv[0]} --start-period {args.start_period} --end-period {args.end_period} --confirm")
            return
        
        # 二次确认
        print("\n⚠️  警告: 此操作将永久删除历史数据，无法恢复！")
        print(f"只会保留期号 {args.start_period} 到 {args.end_period} 的数据，其他期号的数据将被删除。")
        
        confirm = input("\n确认继续吗？(输入 'YES' 确认): ")
        if confirm != 'YES':
            print("操作已取消")
            return
        
        # 执行期号范围清理
        success = cleanup_by_period_range(mongodb_uri, db_name, args.start_period, args.end_period)
        
    elif args.start_period or args.end_period:
        print("错误: --start-period 和 --end-period 必须同时指定")
        return
    elif args.target_date:
        # 按指定日期清理
        target_date = args.target_date
        
        print("数据库清理脚本 - 按日期清理")
        print("=" * 50)
        print(f"MongoDB URI: {mongodb_uri}")
        print(f"数据库名称: {db_name}")
        print(f"保留日期: {target_date}")
        print(f"确认执行: {'是' if args.confirm else '否（预览模式）'}")
        
        if not args.confirm:
            print("\n⚠️  这是预览模式，不会实际删除数据")
            print("要执行实际清理，请添加 --confirm 参数")
            print("\n示例:")
            print(f"  python3 {sys.argv[0]} --target-date {target_date} --confirm")
            return
        
        # 二次确认
        print("\n⚠️  警告: 此操作将永久删除历史数据，无法恢复！")
        print(f"只会保留 {target_date} 的数据，其他日期的数据将被删除。")
        
        confirm = input("\n确认继续吗？(输入 'YES' 确认): ")
        if confirm != 'YES':
            print("操作已取消")
            return
        
        # 执行日期清理
        success = cleanup_database(mongodb_uri, db_name, target_date)
    else:
        # 按天数清理（默认模式）
        keep_days = args.keep_days
        
        print("数据库清理脚本 - 按天数清理")
        print("=" * 50)
        print(f"MongoDB URI: {mongodb_uri}")
        print(f"数据库名称: {db_name}")
        print(f"保留天数: {keep_days} 天")
        print(f"确认执行: {'是' if args.confirm else '否（预览模式）'}")
        
        if not args.confirm:
            print("\n⚠️  这是预览模式，不会实际删除数据")
            print("要执行实际清理，请添加 --confirm 参数")
            print("\n示例:")
            print(f"  python3 {sys.argv[0]} --keep-days {keep_days} --confirm")
            return
        
        # 二次确认
        print("\n⚠️  警告: 此操作将永久删除历史数据，无法恢复！")
        print(f"只会保留最近 {keep_days} 天的数据，更早的数据将被删除。")
        
        confirm = input("\n确认继续吗？(输入 'YES' 确认): ")
        if confirm != 'YES':
            print("操作已取消")
            return
        
        # 执行按天数清理
        success = cleanup_by_days(mongodb_uri, db_name, keep_days)
    
    if success:
        print("\n✓ 数据库清理成功完成！")
    else:
        print("\n✗ 数据库清理失败！")
        sys.exit(1)

if __name__ == '__main__':
    main()