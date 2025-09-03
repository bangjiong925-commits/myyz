#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查自动爬虫运行状态
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def check_crontab():
    """检查crontab任务"""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            cron_lines = result.stdout.strip().split('\n')
            auto_scraper_jobs = [line for line in cron_lines if 'auto_scraper.py' in line and not line.startswith('#')]
            return auto_scraper_jobs
        else:
            return []
    except Exception as e:
        print(f"检查crontab时出错: {e}")
        return []

def check_recent_data():
    """检查最近的数据文件"""
    data_file = Path('data/latest_taiwan_pk10_data.json')
    if not data_file.exists():
        return None, None, None
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            return 0, None, None
        
        # 获取最新记录的时间
        latest_record = data[0]
        scraped_time = datetime.fromisoformat(latest_record['scrapedAt'].replace('Z', '+00:00'))
        
        return len(data), latest_record['period'], scraped_time
    except Exception as e:
        print(f"读取数据文件时出错: {e}")
        return None, None, None

def check_log_files():
    """检查日志文件"""
    log_dir = Path('logs')
    if not log_dir.exists():
        return []
    
    # 获取最近的日志文件
    log_files = list(log_dir.glob('*.log'))
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    recent_logs = []
    for log_file in log_files[:5]:  # 最近5个日志文件
        stat = log_file.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        size = stat.st_size
        recent_logs.append({
            'file': log_file.name,
            'modified': modified_time,
            'size': size
        })
    
    return recent_logs

def main():
    print("=== 台湾PK10自动爬虫状态检查 ===")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查crontab任务
    print("1. Crontab定时任务状态:")
    cron_jobs = check_crontab()
    if cron_jobs:
        print(f"   ✓ 发现 {len(cron_jobs)} 个自动爬虫任务")
        for job in cron_jobs:
            print(f"   - {job}")
    else:
        print("   ✗ 未发现crontab定时任务")
    print()
    
    # 检查数据文件
    print("2. 数据文件状态:")
    record_count, latest_period, scraped_time = check_recent_data()
    if record_count is not None:
        print(f"   ✓ 数据文件存在，包含 {record_count} 条记录")
        print(f"   ✓ 最新期号: {latest_period}")
        if scraped_time:
            time_diff = datetime.now() - scraped_time.replace(tzinfo=None)
            print(f"   ✓ 最后更新: {scraped_time.strftime('%Y-%m-%d %H:%M:%S')} ({time_diff.total_seconds():.0f}秒前)")
            
            # 判断数据是否过期
            if time_diff > timedelta(minutes=10):
                print("   ⚠️  数据可能已过期（超过10分钟未更新）")
            else:
                print("   ✓ 数据较新")
    else:
        print("   ✗ 数据文件不存在或无法读取")
    print()
    
    # 检查日志文件
    print("3. 日志文件状态:")
    recent_logs = check_log_files()
    if recent_logs:
        print(f"   ✓ 发现 {len(recent_logs)} 个日志文件")
        for log in recent_logs[:3]:  # 显示最近3个
            print(f"   - {log['file']}: {log['modified'].strftime('%Y-%m-%d %H:%M:%S')}, {log['size']} bytes")
    else:
        print("   ✗ 未发现日志文件")
    print()
    
    # 运行建议
    print("4. 运行建议:")
    if not cron_jobs and (record_count is None or time_diff > timedelta(minutes=10)):
        print("   建议设置自动运行:")
        print("   - 运行 ./setup_auto_run.sh 设置定时任务")
        print("   - 或手动执行 python3 auto_scraper.py --mode single")
    elif cron_jobs and record_count and time_diff <= timedelta(minutes=10):
        print("   ✓ 系统运行正常")
    elif cron_jobs and time_diff > timedelta(minutes=10):
        print("   ⚠️  定时任务已设置但数据未及时更新，请检查:")
        print("   - 检查cron服务状态: systemctl status cron")
        print("   - 查看cron日志: tail -f logs/cron.log")
        print("   - 手动测试: python3 auto_scraper.py --mode single")
    
    print()
    print("=== 检查完成 ===")

if __name__ == '__main__':
    main()