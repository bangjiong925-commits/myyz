#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动爬虫脚本 - 定时运行数据抓取并保存到MongoDB
"""

import os
import sys
import time
import schedule
import subprocess
from datetime import datetime, time as dt_time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

try:
    from python_scraper import TaiwanPK10Scraper
except ImportError:
    print("错误: 无法导入python_scraper模块")
    print("请确保python_scraper.py文件在当前目录")
    sys.exit(1)

class AutoScraper:
    """自动爬虫管理器"""
    
    def __init__(self, mongodb_uri="mongodb://localhost:27017", db_name="taiwan_pk10"):
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.scraper = None
        self.is_running = False
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
        
        # 同时写入日志文件
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"auto_scraper_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def run_scraper_job(self):
        """执行爬虫任务"""
        if self.is_running:
            self.log("爬虫任务正在运行中，跳过本次执行")
            return
        
        self.is_running = True
        self.log("开始执行爬虫任务")
        
        try:
            # 创建爬虫实例
            self.scraper = TaiwanPK10Scraper(
                headless=True,
                timeout=30,
                mongodb_uri=self.mongodb_uri,
                db_name=self.db_name
            )
            
            # 运行爬虫
            success = self.scraper.run_scraper(max_pages=5)
            
            if success:
                self.log("爬虫任务执行成功")
            else:
                self.log("爬虫任务执行失败")
                
        except Exception as e:
            self.log(f"爬虫任务执行出错: {str(e)}")
        finally:
            if self.scraper:
                try:
                    self.scraper.cleanup()
                except:
                    pass
            self.is_running = False
            self.log("爬虫任务结束")
    
    def run_single_scrape(self):
        """运行单次爬取"""
        self.log("执行单次数据抓取")
        self.run_scraper_job()
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每5分钟执行一次（工作时间）
        schedule.every(5).minutes.do(self.run_scraper_job)
        
        # 也可以设置特定时间执行
        # schedule.every().hour.at(":00").do(self.run_scraper_job)
        # schedule.every().hour.at(":30").do(self.run_scraper_job)
        
        self.log("定时任务已设置: 每5分钟执行一次")
    
    def run_scheduler(self):
        """运行调度器"""
        self.log("自动爬虫调度器启动")
        self.setup_schedule()
        
        # 启动时执行一次
        self.log("执行初始数据抓取")
        self.run_scraper_job()
        
        # 开始调度循环
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # 每30秒检查一次
        except KeyboardInterrupt:
            self.log("收到停止信号，正在关闭调度器")
        except Exception as e:
            self.log(f"调度器运行出错: {str(e)}")
        finally:
            self.log("自动爬虫调度器已停止")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动爬虫脚本')
    parser.add_argument('--mode', choices=['single', 'schedule'], default='schedule',
                       help='运行模式: single(单次) 或 schedule(定时)')
    parser.add_argument('--mongodb-uri',
                       help='MongoDB连接URI')
    parser.add_argument('--db-name',
                       help='数据库名称')
    
    args = parser.parse_args()
    
    # 从环境变量或命令行参数获取配置
    mongodb_uri = args.mongodb_uri or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = args.db_name or os.environ.get('MONGODB_DB_NAME', 'taiwan_pk10')
    
    print(f"自动爬虫启动配置:")
    print(f"  运行模式: {args.mode}")
    print(f"  数据库: {db_name}")
    print(f"  MongoDB URI: {mongodb_uri[:20]}..." if len(mongodb_uri) > 20 else f"  MongoDB URI: {mongodb_uri}")
    
    # 创建自动爬虫实例
    auto_scraper = AutoScraper(
        mongodb_uri=mongodb_uri,
        db_name=db_name
    )
    
    if args.mode == 'single':
        # 单次执行
        auto_scraper.run_single_scrape()
    else:
        # 定时执行
        auto_scraper.run_scheduler()

if __name__ == '__main__':
    main()