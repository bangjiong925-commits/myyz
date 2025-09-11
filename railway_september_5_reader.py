#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway云端定时任务脚本 - 读取2024年9月5日数据
在Railway平台上运行，连接MongoDB Atlas
运行时间：凌晨00:00到早上07:05
"""

import os
import sys
import logging
import subprocess
from datetime import datetime, timezone, timedelta
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/railway_september_5.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class RailwaySeptember5Reader:
    def __init__(self):
        self.target_date = "2024-09-05"
        self.script_path = os.path.join(os.path.dirname(__file__), "read_yesterday_data.py")
        
    def check_time_window(self):
        """检查是否在允许的时间窗口内（凌晨00:00到早上07:05）"""
        # 使用UTC+8时区（台湾时间）
        taiwan_tz = timezone(timedelta(hours=8))
        now = datetime.now(taiwan_tz)
        
        # 检查时间是否在00:00到07:05之间
        if now.hour < 7 or (now.hour == 7 and now.minute <= 5):
            logger.info(f"当前时间 {now.strftime('%H:%M:%S')} 在允许的执行窗口内")
            return True
        else:
            logger.info(f"当前时间 {now.strftime('%H:%M:%S')} 不在执行窗口内（00:00-07:05）")
            return False
    
    def check_environment(self):
        """检查Railway环境变量"""
        required_vars = ['MONGODB_URI']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
            return False
        
        logger.info("环境变量检查通过")
        return True
    
    def run_data_reader(self):
        """执行数据读取脚本"""
        try:
            if not os.path.exists(self.script_path):
                logger.error(f"数据读取脚本不存在: {self.script_path}")
                return False
            
            # 构建命令
            cmd = [sys.executable, self.script_path, "--date", self.target_date]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 执行脚本
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                logger.info("数据读取脚本执行成功")
                if result.stdout:
                    logger.info(f"输出: {result.stdout}")
                return True
            else:
                logger.error(f"数据读取脚本执行失败，返回码: {result.returncode}")
                if result.stderr:
                    logger.error(f"错误信息: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("数据读取脚本执行超时")
            return False
        except Exception as e:
            logger.error(f"执行数据读取脚本时发生异常: {str(e)}")
            return False
    
    def run(self):
        """主执行函数"""
        logger.info("=== Railway云端定时任务开始 ===")
        logger.info(f"目标日期: {self.target_date}")
        
        # 检查时间窗口
        if not self.check_time_window():
            logger.info("不在执行时间窗口内，任务结束")
            return
        
        # 检查环境变量
        if not self.check_environment():
            logger.error("环境检查失败，任务终止")
            return
        
        # 执行数据读取
        success = self.run_data_reader()
        
        if success:
            logger.info("=== Railway云端定时任务完成 ===")
        else:
            logger.error("=== Railway云端定时任务失败 ===")

def main():
    """主函数"""
    try:
        reader = RailwaySeptember5Reader()
        reader.run()
    except Exception as e:
        logger.error(f"主函数执行异常: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()