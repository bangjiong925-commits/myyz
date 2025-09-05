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
from datetime import datetime, time as dt_time, timedelta
from pathlib import Path
import threading
import json
import random

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
    
    def __init__(self, mongodb_uri=None, db_name="taiwan_pk10"):
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.scraper = None
        self.is_running = False
        self.last_period_number = None
        self.countdown_timer = None
        self.smart_schedule_enabled = True
        # 设置运行时间范围：7:05 到 23:59
        self.start_time = dt_time(7, 5)  # 7:05
        self.end_time = dt_time(23, 59)  # 23:59
        
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
    
    def is_within_operating_hours(self):
        """检查当前时间是否在运行时间范围内（7:05-23:59）"""
        current_time = datetime.now().time()
        return self.start_time <= current_time <= self.end_time
    
    def get_random_interval(self):
        """获取随机间隔时间（30-60秒）"""
        return random.randint(30, 60)
    
    def run_scraper_job(self):
        """执行爬虫任务"""
        # 检查是否在运行时间范围内
        if not self.is_within_operating_hours():
            current_time = datetime.now().strftime('%H:%M:%S')
            self.log(f"当前时间 {current_time} 不在运行时间范围内（7:05-23:59），跳过执行")
            return
        
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
            
            # 抓取今天的完整数据
            from datetime import datetime
            today = datetime.now()
            all_data = self.scraper.run_scraper(
                target_date=today,
                max_pages=10,  # 抓取更多页面以获取完整数据
                save_to_file=True,
                save_to_db=True
            )
            
            if all_data:
                self.log(f"成功抓取今日完整数据，共 {len(all_data)} 条记录")
                
                # 获取最新一条记录的期号
                latest_record = all_data[0] if all_data else None
                if latest_record:
                    current_period = latest_record.period
                    draw_time = latest_record.draw_time
                    
                    # 检查是否有新数据
                    if self.last_period_number and current_period == self.last_period_number:
                        self.log(f"暂无新数据，当前期号: {current_period}")
                        # 如果没有新数据，60秒后重试
                        if self.smart_schedule_enabled:
                            self.schedule_next_scrape(60)
                    else:
                        self.log(f"获取到新数据 - 期号: {current_period}, 开奖时间: {draw_time}")
                        self.last_period_number = current_period
                        
                        # 根据开奖时间安排下次抓取（140秒后）
                        if self.smart_schedule_enabled:
                            self.schedule_next_scrape_from_draw_time(draw_time)
                
                self.log("爬虫任务执行成功")
            else:
                self.log("爬虫任务执行失败 - 未获取到数据")
                # 失败时60秒后重试
                if self.smart_schedule_enabled:
                    self.schedule_next_scrape(60)
                
        except Exception as e:
            self.log(f"爬虫任务执行出错: {str(e)}")
            # 出错时60秒后重试
            if self.smart_schedule_enabled:
                self.schedule_next_scrape(60)
        finally:
            if self.scraper:
                try:
                    self.scraper.cleanup()
                except:
                    pass
            self.is_running = False
            self.log("爬虫任务结束")
    
    def save_latest_data(self, data):
        """保存最新数据到本地文件"""
        try:
            # 保存到latest_data.json
            latest_file = Path('data/latest_data.json')
            latest_file.parent.mkdir(exist_ok=True)
            
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.log(f"最新数据已保存到 {latest_file}")
        except Exception as e:
            self.log(f"保存最新数据失败: {str(e)}")
    
    def schedule_next_scrape(self, seconds):
        """安排下次抓取（指定秒数后）"""
        if self.countdown_timer:
            self.countdown_timer.cancel()
        
        # 检查安排的时间是否在运行时间范围内
        future_time = datetime.now() + timedelta(seconds=seconds)
        future_time_only = future_time.time()
        
        if self.start_time <= future_time_only <= self.end_time:
            self.log(f"安排 {seconds} 秒后进行下次抓取（{future_time.strftime('%H:%M:%S')}）")
            self.countdown_timer = threading.Timer(seconds, self.run_scraper_job)
            self.countdown_timer.start()
        else:
            # 如果安排的时间超出运行范围，计算到明天7:05的等待时间
            tomorrow_start = datetime.now().replace(hour=7, minute=5, second=0, microsecond=0) + timedelta(days=1)
            wait_until_tomorrow = (tomorrow_start - datetime.now()).total_seconds()
            self.log(f"安排的时间 {future_time.strftime('%H:%M:%S')} 超出运行范围，将在明天7:05重新开始")
            self.countdown_timer = threading.Timer(wait_until_tomorrow, self.run_scraper_job)
            self.countdown_timer.start()
    
    def schedule_next_scrape_from_draw_time(self, draw_time):
        """根据开奖时间安排下次抓取（开奖时间+140秒）"""
        try:
            # 解析开奖时间
            now = datetime.now()
            
            # 如果draw_time只包含时间（HH:MM:SS），使用今天的日期
            if ':' in draw_time and len(draw_time.split(':')) >= 2:
                time_parts = draw_time.split(':')
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                
                # 构造开奖时间
                draw_datetime = now.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
                
                # 如果开奖时间是明天（跨日情况）
                if draw_datetime < now - timedelta(hours=12):
                    draw_datetime += timedelta(days=1)
                
                # 计算下次抓取时间（开奖时间 + 140秒）
                next_scrape_time = draw_datetime + timedelta(seconds=140)
                
                # 计算等待时间
                wait_seconds = (next_scrape_time - now).total_seconds()
                
                if wait_seconds > 0:
                    self.log(f"开奖时间: {draw_datetime.strftime('%H:%M:%S')}, 下次抓取时间: {next_scrape_time.strftime('%H:%M:%S')}, 等待 {int(wait_seconds)} 秒")
                    self.schedule_next_scrape(int(wait_seconds))
                else:
                    # 如果计算出的时间已经过去，立即抓取
                    self.log("开奖时间已过，立即进行下次抓取")
                    self.schedule_next_scrape(5)
            else:
                # 如果时间格式不正确，使用默认140秒
                self.log(f"无法解析开奖时间格式: {draw_time}，使用默认140秒间隔")
                self.schedule_next_scrape(140)
                
        except Exception as e:
            self.log(f"计算下次抓取时间失败: {str(e)}，使用默认140秒间隔")
            self.schedule_next_scrape(140)
    
    def run_single_scrape(self):
        """运行单次爬取"""
        self.log("执行单次数据抓取")
        self.smart_schedule_enabled = False  # 单次模式不启用智能调度
        self.run_scraper_job()
    
    def setup_schedule(self):
        """设置定时任务（传统模式）"""
        # 使用随机间隔（30-60秒）
        interval = self.get_random_interval()
        schedule.every(interval).seconds.do(self.run_scraper_job)
        
        self.log(f"定时任务已设置: 每{interval}秒执行一次（传统模式，运行时间：7:05-23:59）")
    
    def run_scheduler(self):
        """运行调度器"""
        self.log("自动爬虫调度器启动（智能调度模式）")
        
        # 启动时执行一次
        self.log("执行初始数据抓取")
        self.run_scraper_job()
        
        # 智能调度模式：基于开奖时间动态调整
        try:
            while True:
                time.sleep(10)  # 每10秒检查一次状态
                # 在智能调度模式下，主要通过Timer来控制抓取时机
                # 这里只需要保持程序运行
        except KeyboardInterrupt:
            self.log("收到停止信号，正在关闭调度器")
            if self.countdown_timer:
                self.countdown_timer.cancel()
        except Exception as e:
            self.log(f"调度器运行出错: {str(e)}")
        finally:
            if self.countdown_timer:
                self.countdown_timer.cancel()
            self.log("自动爬虫调度器已停止")
    
    def run_traditional_scheduler(self):
        """运行传统调度器（随机间隔30-60秒）"""
        self.log("自动爬虫调度器启动（传统模式，运行时间：7:05-23:59）")
        self.smart_schedule_enabled = False
        
        # 启动时执行一次（如果在运行时间内）
        if self.is_within_operating_hours():
            self.log("执行初始数据抓取")
            self.run_scraper_job()
        else:
            current_time = datetime.now().strftime('%H:%M:%S')
            self.log(f"当前时间 {current_time} 不在运行时间范围内，等待到7:05开始")
        
        # 开始调度循环
        try:
            last_schedule_time = 0
            while True:
                current_time = time.time()
                
                # 每次重新设置随机间隔的调度
                if current_time - last_schedule_time > 60:  # 每分钟重新设置一次调度
                    schedule.clear()  # 清除之前的调度
                    if self.is_within_operating_hours():
                        self.setup_schedule()
                    last_schedule_time = current_time
                
                schedule.run_pending()
                time.sleep(10)  # 每10秒检查一次
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
    parser.add_argument('--mode', choices=['single', 'smart', 'traditional'], default='smart',
                       help='运行模式: single(单次), smart(智能调度), traditional(传统定时)')
    parser.add_argument('--mongodb-uri',
                       help='MongoDB连接URI')
    parser.add_argument('--db-name',
                       help='数据库名称')
    
    args = parser.parse_args()
    
    # 从环境变量或命令行参数获取配置
    mongodb_uri = args.mongodb_uri or os.environ.get('MONGODB_URI')
    db_name = args.db_name or os.environ.get('MONGODB_DB_NAME', 'taiwan_pk10')
    
    print(f"自动爬虫启动配置:")
    print(f"  运行模式: {args.mode}")
    print(f"  数据库: {db_name}")
    print(f"  MongoDB URI: {mongodb_uri[:20]}..." if len(mongodb_uri) > 20 else f"  MongoDB URI: {mongodb_uri}")
    
    if args.mode == 'smart':
        print(f"  调度策略: 基于开奖时间后140秒智能调度（运行时间：7:05-23:59）")
    elif args.mode == 'traditional':
        print(f"  调度策略: 每30-60秒随机间隔（运行时间：7:05-23:59）")
    
    # 创建自动爬虫实例
    auto_scraper = AutoScraper(
        mongodb_uri=mongodb_uri,
        db_name=db_name
    )
    
    if args.mode == 'single':
        # 单次执行
        auto_scraper.run_single_scrape()
    elif args.mode == 'smart':
        # 智能调度执行
        auto_scraper.run_scheduler()
    else:
        # 传统定时执行
        auto_scraper.run_traditional_scheduler()

if __name__ == '__main__':
    main()