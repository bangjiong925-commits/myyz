#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时间控制功能
"""

import sys
from datetime import datetime, time as dt_time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from auto_scraper import AutoScraper

def test_time_control():
    """测试时间控制功能"""
    print("=== 测试时间控制功能 ===")
    
    # 创建AutoScraper实例
    scraper = AutoScraper()
    
    # 测试当前时间
    current_time = datetime.now().time()
    print(f"当前时间: {current_time.strftime('%H:%M:%S')}")
    print(f"运行时间范围: {scraper.start_time.strftime('%H:%M:%S')} - {scraper.end_time.strftime('%H:%M:%S')}")
    
    # 检查是否在运行时间内
    is_within = scraper.is_within_operating_hours()
    print(f"是否在运行时间内: {is_within}")
    
    # 测试随机间隔
    print("\n=== 测试随机间隔功能 ===")
    for i in range(5):
        interval = scraper.get_random_interval()
        print(f"随机间隔 {i+1}: {interval} 秒")
    
    # 测试不同时间点
    print("\n=== 测试不同时间点 ===")
    test_times = [
        dt_time(6, 30),   # 6:30 - 应该不在范围内
        dt_time(7, 5),    # 7:05 - 应该在范围内
        dt_time(12, 0),   # 12:00 - 应该在范围内
        dt_time(23, 59),  # 23:59 - 应该在范围内
        dt_time(0, 30),   # 0:30 - 应该不在范围内
    ]
    
    for test_time in test_times:
        # 临时修改当前时间进行测试
        original_start = scraper.start_time
        original_end = scraper.end_time
        
        # 模拟检查
        is_within = original_start <= test_time <= original_end
        print(f"时间 {test_time.strftime('%H:%M:%S')}: {'在范围内' if is_within else '不在范围内'}")

if __name__ == '__main__':
    test_time_control()