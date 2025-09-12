#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台湾PK10每日数据获取器 - API版本
使用API接口获取数据，替代爬虫方案
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import json

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_scraper import TaiwanPK10APIClient

class DailyScraper:
    """每日数据获取器"""
    
    def __init__(self, mongodb_uri: str = None):
        self.mongodb_uri = mongodb_uri or os.getenv('MONGODB_URI')
        self.api_client = TaiwanPK10APIClient(mongodb_uri=self.mongodb_uri)
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志记录"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"daily_scraper_{today}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("每日数据获取器启动")
    
    def get_data_for_date(self, date: str, retry_count: int = 3) -> Optional[Dict]:
        """获取指定日期的数据，带重试机制
        
        Args:
            date: 日期字符串，格式为 YYYY-MM-DD
            retry_count: 重试次数
            
        Returns:
            数据字典或None
        """
        for attempt in range(retry_count):
            try:
                self.logger.info(f"尝试获取 {date} 的数据 (第 {attempt + 1} 次)")
                result = self.api_client.get_data_for_date(date)
                
                if result and result.get('count', 0) > 0:
                    self.logger.info(f"成功获取 {date} 的数据，共 {result['count']} 条记录")
                    return result
                else:
                    self.logger.warning(f"获取 {date} 的数据为空")
                    
            except Exception as e:
                self.logger.error(f"获取 {date} 数据失败 (第 {attempt + 1} 次): {e}")
                
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5  # 递增等待时间
                    self.logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
        
        self.logger.error(f"获取 {date} 数据失败，已重试 {retry_count} 次")
        return None
    
    def run_daily_task(self) -> Dict:
        """执行每日数据获取任务
        
        Returns:
            任务执行结果
        """
        self.logger.info("开始执行每日数据获取任务")
        
        # 获取今天和昨天的日期
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        results = {
            'today': None,
            'yesterday': None,
            'total_count': 0,
            'success': False
        }
        
        # 获取昨天的数据
        self.logger.info(f"获取昨天 ({yesterday}) 的数据")
        yesterday_result = self.get_data_for_date(yesterday)
        if yesterday_result:
            results['yesterday'] = yesterday_result
            results['total_count'] += yesterday_result.get('count', 0)
            self.logger.info(f"昨天数据获取成功: {yesterday_result.get('count', 0)} 条记录")
        else:
            self.logger.warning("昨天数据获取失败")
        
        # 获取今天的数据
        self.logger.info(f"获取今天 ({today}) 的数据")
        today_result = self.get_data_for_date(today)
        if today_result:
            results['today'] = today_result
            results['total_count'] += today_result.get('count', 0)
            self.logger.info(f"今天数据获取成功: {today_result.get('count', 0)} 条记录")
        else:
            self.logger.warning("今天数据获取失败")
        
        # 判断任务是否成功
        if results['today'] or results['yesterday']:
            results['success'] = True
            self.logger.info(f"每日数据获取任务完成，总计获取 {results['total_count']} 条记录")
        else:
            self.logger.error("每日数据获取任务失败，没有获取到任何数据")
        
        return results
    
    def test_api_connection(self) -> bool:
        """测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            self.logger.info("测试API连接...")
            
            # 测试获取今天的数据
            today = datetime.now().strftime("%Y-%m-%d")
            result = self.api_client.fetch_data_by_date(today)
            
            if result is not None:
                self.logger.info(f"API连接测试成功，获取到 {len(result)} 条记录")
                return True
            else:
                # 如果今天没有数据，尝试昨天
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                result = self.api_client.fetch_data_by_date(yesterday)
                
                if result is not None:
                    self.logger.info(f"API连接测试成功（使用昨天数据），获取到 {len(result)} 条记录")
                    return True
                else:
                    self.logger.error("API连接测试失败，无法获取数据")
                    return False
                    
        except Exception as e:
            self.logger.error(f"API连接测试失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.api_client:
            self.api_client.close()
        self.logger.info("每日数据获取器已关闭")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="台湾PK10每日数据获取器")
    parser.add_argument("--test", action="store_true", help="测试API连接")
    parser.add_argument("--date", help="获取指定日期的数据 (YYYY-MM-DD)")
    parser.add_argument("--mongodb-uri", help="MongoDB连接URI")
    
    args = parser.parse_args()
    
    # 从环境变量或参数获取MongoDB URI
    mongodb_uri = args.mongodb_uri or os.getenv('MONGODB_URI')
    
    # 创建数据获取器
    scraper = DailyScraper(mongodb_uri=mongodb_uri)
    
    try:
        if args.test:
            # 测试API连接
            success = scraper.test_api_connection()
            if success:
                print("API连接测试成功")
                exit(0)
            else:
                print("API连接测试失败")
                exit(1)
        
        elif args.date:
            # 获取指定日期的数据
            result = scraper.get_data_for_date(args.date)
            if result:
                print(f"成功获取 {args.date} 的数据，共 {result['count']} 条记录")
                print(f"数据已保存到: {result.get('json_file', 'N/A')}")
                if result.get('db_saved'):
                    print("数据已保存到MongoDB")
            else:
                print(f"获取 {args.date} 的数据失败")
                exit(1)
        
        else:
            # 执行每日任务
            results = scraper.run_daily_task()
            
            if results['success']:
                print(f"每日数据获取任务完成，总计 {results['total_count']} 条记录")
                
                if results['yesterday']:
                    print(f"昨天数据: {results['yesterday']['count']} 条记录")
                
                if results['today']:
                    print(f"今天数据: {results['today']['count']} 条记录")
            else:
                print("每日数据获取任务失败")
                exit(1)
                
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"程序执行出错: {e}")
        exit(1)
    finally:
        scraper.close()

if __name__ == "__main__":
    main()