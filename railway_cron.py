#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway云端Cron Job服务
用于在Railway平台上运行定时任务
每小时检查一次，在指定时间窗口内执行9月5日数据读取任务
"""

import os
import sys
import time
import logging
import schedule
import subprocess
from datetime import datetime, timezone, timedelta

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/railway_cron.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class RailwayCronService:
    def __init__(self):
        self.reader_script = os.path.join(os.path.dirname(__file__), "railway_september_5_reader.py")
        self.taiwan_tz = timezone(timedelta(hours=8))
        
    def is_in_execution_window(self):
        """检查是否在执行时间窗口内（凌晨00:00到早上07:05）"""
        now = datetime.now(self.taiwan_tz)
        
        # 检查时间是否在00:00到07:05之间
        if now.hour < 7 or (now.hour == 7 and now.minute <= 5):
            return True
        return False
    
    def run_september_5_task(self):
        """执行9月5日数据读取任务"""
        try:
            logger.info("检查是否需要执行9月5日数据读取任务")
            
            # 检查时间窗口
            if not self.is_in_execution_window():
                logger.info("当前时间不在执行窗口内，跳过任务")
                return
            
            # 检查脚本是否存在
            if not os.path.exists(self.reader_script):
                logger.error(f"读取脚本不存在: {self.reader_script}")
                return
            
            logger.info("开始执行9月5日数据读取任务")
            
            # 执行脚本
            result = subprocess.run(
                [sys.executable, self.reader_script],
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                logger.info("9月5日数据读取任务执行成功")
                if result.stdout:
                    logger.info(f"任务输出: {result.stdout}")
            else:
                logger.error(f"9月5日数据读取任务执行失败，返回码: {result.returncode}")
                if result.stderr:
                    logger.error(f"错误信息: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            logger.error("9月5日数据读取任务执行超时")
        except Exception as e:
            logger.error(f"执行9月5日数据读取任务时发生异常: {str(e)}")
    
    def setup_schedule(self):
        """设置定时任务调度"""
        # 每小时检查一次，在执行窗口内运行任务
        schedule.every().hour.do(self.run_september_5_task)
        
        # 在特定时间点也执行任务（确保不会错过）
        schedule.every().day.at("01:00").do(self.run_september_5_task)
        schedule.every().day.at("03:00").do(self.run_september_5_task)
        schedule.every().day.at("05:00").do(self.run_september_5_task)
        schedule.every().day.at("07:00").do(self.run_september_5_task)
        
        logger.info("定时任务调度已设置")
        logger.info("- 每小时检查一次执行条件")
        logger.info("- 每天01:00, 03:00, 05:00, 07:00执行任务")
    
    def run_service(self):
        """运行cron服务"""
        logger.info("=== Railway Cron服务启动 ===")
        
        # 设置定时任务
        self.setup_schedule()
        
        # 立即执行一次检查
        self.run_september_5_task()
        
        # 开始调度循环
        logger.info("开始定时任务调度循环")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
                # 每小时输出一次状态
                now = datetime.now(self.taiwan_tz)
                if now.minute == 0:
                    logger.info(f"Cron服务运行中 - 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                    
            except KeyboardInterrupt:
                logger.info("收到中断信号，停止Cron服务")
                break
            except Exception as e:
                logger.error(f"Cron服务运行异常: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再继续

def main():
    """主函数"""
    try:
        cron_service = RailwayCronService()
        cron_service.run_service()
    except Exception as e:
        logger.error(f"Cron服务启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()