#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时读取2024年9月5日数据的脚本
在凌晨00:00到早上07:05之间运行
"""

import os
import sys
import subprocess
from datetime import datetime, time
import logging
from pathlib import Path

# 设置日志
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/read_september_5_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_valid_time_range():
    """检查当前时间是否在允许的运行时间范围内（00:00-07:05）"""
    current_time = datetime.now().time()
    start_time = time(0, 0)  # 00:00
    end_time = time(7, 5)    # 07:05
    
    return start_time <= current_time <= end_time

def run_data_reader():
    """运行数据读取脚本"""
    try:
        # 检查时间范围
        if not is_valid_time_range():
            current_time = datetime.now().strftime('%H:%M:%S')
            logger.warning(f"当前时间 {current_time} 不在允许的运行时间范围内（00:00-07:05）")
            return False
        
        logger.info("开始读取2024年9月5日的数据")
        
        # 构建命令
        script_path = Path(__file__).parent / 'read_yesterday_data.py'
        cmd = [sys.executable, str(script_path), '--date', '2024-09-05']
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            logger.info("数据读取成功")
            if result.stdout:
                logger.info(f"输出: {result.stdout}")
            return True
        else:
            logger.error(f"数据读取失败，返回码: {result.returncode}")
            if result.stderr:
                logger.error(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"执行数据读取时发生异常: {str(e)}")
        return False

def main():
    """主函数"""
    try:
        logger.info("定时任务启动 - 读取2024年9月5日数据")
        
        # 检查环境变量
        if not os.environ.get('MONGODB_URI'):
            logger.error("MONGODB_URI环境变量未设置")
            sys.exit(1)
        
        # 运行数据读取
        success = run_data_reader()
        
        if success:
            logger.info("定时任务执行成功")
        else:
            logger.error("定时任务执行失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"定时任务执行异常: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()