#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取指定日期数据的脚本
在凌晨到早上7:05期间运行，从数据库中读取指定日期的开奖数据
支持通过命令行参数指定日期，默认为昨天
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import pymongo
from pymongo import MongoClient
import logging

# 设置日志 - 适配Railway云环境
log_handlers = [logging.StreamHandler()]

# 在Railway环境中使用/tmp目录，本地环境使用logs目录
if os.environ.get('RAILWAY_ENVIRONMENT'):
    log_file = '/tmp/read_yesterday_data.log'
else:
    # 本地环境，确保logs目录存在
    os.makedirs('logs', exist_ok=True)
    log_file = 'logs/read_yesterday_data.log'

log_handlers.append(logging.FileHandler(log_file))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

class DateDataReader:
    def __init__(self, mongodb_uri=None, db_name='taiwan_pk10', target_date=None):
        """
        初始化指定日期数据读取器
        
        Args:
            mongodb_uri: MongoDB连接URI
            db_name: 数据库名称
            target_date: 目标日期，默认为昨天
        """
        self.mongodb_uri = mongodb_uri or os.environ.get('MONGODB_URI')
        self.db_name = db_name
        self.target_date = target_date or (datetime.now() - timedelta(days=1))
        self.client = None
        self.db = None
        
        if not self.mongodb_uri:
            raise ValueError("MongoDB URI未配置，请设置MONGODB_URI环境变量")
    
    def connect_to_database(self):
        """连接到MongoDB数据库"""
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.db_name]
            # 测试连接
            self.client.admin.command('ping')
            logger.info(f"成功连接到MongoDB数据库: {self.db_name}")
            return True
        except Exception as e:
            logger.error(f"连接数据库失败: {str(e)}")
            return False
    
    def get_target_date_range(self):
        """获取目标日期的日期范围"""
        # 目标日期的开始时间（00:00:00）
        start_date = self.target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 目标日期的结束时间（23:59:59）
        end_date = self.target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        logger.info(f"查询目标日期数据范围: {start_date.strftime('%Y-%m-%d %H:%M:%S')} 到 {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return start_date, end_date
    
    def read_target_date_data(self):
        """读取目标日期的开奖数据"""
        try:
            if not self.connect_to_database():
                return None
            
            start_date, end_date = self.get_target_date_range()
            
            # 查询目标日期的数据
            collection = self.db.lottery_results
            
            # 构建查询条件
            query = {
                'timestamp': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            # 执行查询，按时间排序
            cursor = collection.find(query).sort('timestamp', 1)
            
            # 收集数据
            data_list = []
            for doc in cursor:
                # 转换ObjectId为字符串
                doc['_id'] = str(doc['_id'])
                data_list.append(doc)
            
            logger.info(f"成功读取到 {len(data_list)} 条数据")
            
            # 保存数据到文件
            self.save_data_to_file(data_list)
            
            return data_list
            
        except Exception as e:
            logger.error(f"读取数据失败: {str(e)}")
            return None
        finally:
            if self.client:
                self.client.close()
                logger.info("数据库连接已关闭")
    
    def save_data_to_file(self, data_list):
        """保存数据到文件"""
        try:
            # 创建输出目录
            output_dir = Path('data/daily_exports')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            date_str = self.target_date.strftime('%Y-%m-%d')
            filename = f"lottery_data_{date_str}.json"
            filepath = output_dir / filename
            
            # 保存数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"数据已保存到文件: {filepath}")
            
        except Exception as e:
            logger.error(f"保存数据到文件失败: {str(e)}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='读取指定日期的开奖数据')
    parser.add_argument(
        '--date',
        type=str,
        help='指定日期，格式: YYYY-MM-DD (例如: 2024-09-05)，默认为昨天'
    )
    parser.add_argument(
        '--days-ago',
        type=int,
        help='指定几天前的数据，例如: 1表示昨天，2表示前天'
    )
    return parser.parse_args()


def get_target_date(args):
    """根据参数获取目标日期"""
    if args.date:
        try:
            return datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            logger.error("日期格式错误，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
    elif args.days_ago:
        return datetime.now() - timedelta(days=args.days_ago)
    else:
        # 默认为昨天
        return datetime.now() - timedelta(days=1)


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 获取目标日期
        target_date = get_target_date(args)
        
        logger.info(f"开始读取 {target_date.strftime('%Y-%m-%d')} 的开奖数据")
        
        # 创建数据读取器
        reader = DateDataReader(target_date=target_date)
        
        # 读取数据
        data = reader.read_target_date_data()
        
        if data:
            logger.info(f"数据读取完成，共 {len(data)} 条记录")
        else:
            logger.warning("未读取到任何数据")
            
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()