#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台湾PK10 API数据获取器
使用API接口获取数据，替代Selenium爬虫方案
"""

import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import pymongo
from loguru import logger

@dataclass
class LotteryData:
    """彩票数据结构"""
    issue: str  # 期号
    draw_time: str  # 开奖时间
    numbers: List[int]  # 开奖号码
    sum_fs: int  # 前三和值
    sum_big_small: int  # 大小比
    sum_single_double: int  # 单双比
    first_dt: int  # 第一名龙虎
    second_dt: int  # 第二名龙虎
    third_dt: int  # 第三名龙虎
    fourth_dt: int  # 第四名龙虎
    fifth_dt: int  # 第五名龙虎
    group_code: int  # 组选代码

class TaiwanPK10APIClient:
    """台湾PK10 API客户端"""
    
    def __init__(self, mongodb_uri: str = None, db_name: str = "lottery_db"):
        self.base_url = "https://api.api68.com/pks/getPksHistoryList.do"
        self.lot_code = "10057"
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.mongo_client = None
        self.db = None
        
        # 设置日志
        self.setup_logging()
        
        # 连接MongoDB
        if self.mongodb_uri:
            self.connect_mongodb()
    
    def setup_logging(self):
        """设置日志记录"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
        log_file = os.path.join(log_dir, f"api_scraper_{timestamp}.log")
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            rotation="10 MB"
        )
        
        logger.info("API数据获取器启动")
    
    def connect_mongodb(self):
        """连接MongoDB数据库"""
        try:
            self.mongo_client = pymongo.MongoClient(self.mongodb_uri)
            self.db = self.mongo_client[self.db_name]
            logger.info(f"成功连接到MongoDB数据库: {self.db_name}")
        except Exception as e:
            logger.error(f"连接MongoDB失败: {e}")
            self.mongo_client = None
            self.db = None
    
    def fetch_data_by_date(self, date: str) -> Optional[List[LotteryData]]:
        """根据日期获取数据
        
        Args:
            date: 日期字符串，格式为 YYYY-MM-DD
            
        Returns:
            LotteryData对象列表，如果失败返回None
        """
        try:
            url = f"{self.base_url}?lotCode={self.lot_code}&date={date}"
            logger.info(f"请求API: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errorCode') != 0:
                logger.error(f"API返回错误: {data.get('message')}")
                return None
            
            result = data.get('result', {})
            if result.get('businessCode') != 0:
                logger.error(f"业务逻辑错误: {result.get('message')}")
                return None
            
            lottery_data_list = []
            for item in result.get('data', []):
                # 解析开奖号码
                numbers = [int(x) for x in item['preDrawCode'].split(',')]
                
                lottery_data = LotteryData(
                    issue=str(item['preDrawIssue']),
                    draw_time=item['preDrawTime'],
                    numbers=numbers,
                    sum_fs=item['sumFS'],
                    sum_big_small=item['sumBigSamll'],
                    sum_single_double=item['sumSingleDouble'],
                    first_dt=item['firstDT'],
                    second_dt=item['secondDT'],
                    third_dt=item['thirdDT'],
                    fourth_dt=item['fourthDT'],
                    fifth_dt=item['fifthDT'],
                    group_code=item['groupCode']
                )
                lottery_data_list.append(lottery_data)
            
            logger.info(f"成功获取 {date} 的数据，共 {len(lottery_data_list)} 条记录")
            return lottery_data_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取数据时发生未知错误: {e}")
            return None
    
    def save_to_json(self, data: List[LotteryData], date: str) -> str:
        """保存数据到JSON文件
        
        Args:
            data: 彩票数据列表
            date: 日期字符串
            
        Returns:
            保存的文件路径
        """
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"taiwan_pk10_data_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)
        
        # 转换为字典格式
        data_dict = {
            "date": date,
            "timestamp": timestamp,
            "count": len(data),
            "data": [asdict(item) for item in data]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到文件: {filepath}")
        return filepath
    
    def save_to_mongodb(self, data: List[LotteryData], date: str) -> bool:
        """保存数据到MongoDB
        
        Args:
            data: 彩票数据列表
            date: 日期字符串
            
        Returns:
            是否保存成功
        """
        if not self.db:
            logger.warning("MongoDB未连接，跳过数据库保存")
            return False
        
        try:
            collection = self.db.taiwan_pk10_data
            
            # 删除当天的旧数据
            delete_result = collection.delete_many({"date": date})
            if delete_result.deleted_count > 0:
                logger.info(f"删除了 {delete_result.deleted_count} 条旧数据")
            
            # 插入新数据
            documents = []
            for item in data:
                doc = asdict(item)
                doc["date"] = date
                doc["created_at"] = datetime.now()
                documents.append(doc)
            
            if documents:
                insert_result = collection.insert_many(documents)
                logger.info(f"成功插入 {len(insert_result.inserted_ids)} 条数据到MongoDB")
                return True
            else:
                logger.warning("没有数据需要插入")
                return False
                
        except Exception as e:
            logger.error(f"保存到MongoDB失败: {e}")
            return False
    
    def get_data_for_date(self, date: str) -> Optional[Dict]:
        """获取指定日期的数据并保存
        
        Args:
            date: 日期字符串，格式为 YYYY-MM-DD
            
        Returns:
            包含数据和统计信息的字典
        """
        logger.info(f"开始获取 {date} 的数据")
        
        # 从API获取数据
        data = self.fetch_data_by_date(date)
        if not data:
            logger.error(f"获取 {date} 的数据失败")
            return None
        
        # 保存到文件
        json_file = self.save_to_json(data, date)
        
        # 保存到数据库
        db_saved = self.save_to_mongodb(data, date)
        
        result = {
            "date": date,
            "count": len(data),
            "data": [asdict(item) for item in data],
            "json_file": json_file,
            "db_saved": db_saved
        }
        
        logger.info(f"完成 {date} 数据获取，共 {len(data)} 条记录")
        return result
    
    def get_today_data(self) -> Optional[Dict]:
        """获取今天的数据"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_data_for_date(today)
    
    def get_yesterday_data(self) -> Optional[Dict]:
        """获取昨天的数据"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return self.get_data_for_date(yesterday)
    
    def get_recent_data(self, days: int = 7) -> Dict:
        """获取最近几天的数据
        
        Args:
            days: 天数
            
        Returns:
            包含所有日期数据的字典
        """
        results = {}
        total_count = 0
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            result = self.get_data_for_date(date)
            if result:
                results[date] = result
                total_count += result['count']
            else:
                results[date] = None
        
        logger.info(f"完成最近 {days} 天数据获取，总计 {total_count} 条记录")
        return {
            "total_days": days,
            "total_count": total_count,
            "results": results
        }
    
    def close(self):
        """关闭连接"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB连接已关闭")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="台湾PK10 API数据获取器")
    parser.add_argument("--date", help="指定日期 (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=1, help="获取最近几天的数据")
    parser.add_argument("--mongodb-uri", help="MongoDB连接URI")
    
    args = parser.parse_args()
    
    # 从环境变量获取MongoDB URI
    mongodb_uri = args.mongodb_uri or os.getenv('MONGODB_URI')
    
    # 创建API客户端
    client = TaiwanPK10APIClient(mongodb_uri=mongodb_uri)
    
    try:
        if args.date:
            # 获取指定日期的数据
            result = client.get_data_for_date(args.date)
            if result:
                print(f"成功获取 {args.date} 的数据，共 {result['count']} 条记录")
            else:
                print(f"获取 {args.date} 的数据失败")
        else:
            # 获取最近几天的数据
            results = client.get_recent_data(args.days)
            print(f"完成最近 {args.days} 天数据获取，总计 {results['total_count']} 条记录")
            
    finally:
        client.close()

if __name__ == "__main__":
    main()