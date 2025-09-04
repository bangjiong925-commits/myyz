#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志文件清理脚本
清理超过指定天数的旧日志文件
"""

import os
import glob
import time
from datetime import datetime, timedelta

def cleanup_logs(log_dir="./logs", days_to_keep=7, dry_run=True):
    """
    清理日志文件
    
    Args:
        log_dir: 日志目录路径
        days_to_keep: 保留天数
        dry_run: 是否为试运行模式
    """
    print(f"日志清理工具 - {'试运行模式' if dry_run else '实际清理模式'}")
    print("=" * 50)
    
    if not os.path.exists(log_dir):
        print(f"日志目录不存在: {log_dir}")
        return
    
    # 计算截止时间
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    cutoff_date = datetime.fromtimestamp(cutoff_time)
    
    print(f"日志目录: {log_dir}")
    print(f"保留天数: {days_to_keep} 天")
    print(f"清理截止时间: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 查找所有日志文件
    log_patterns = [
        os.path.join(log_dir, "*.log"),
        os.path.join(log_dir, "*.log.*"),
        os.path.join(log_dir, "scraper_*.log")
    ]
    
    files_to_delete = []
    total_size = 0
    kept_files = 0
    kept_size = 0
    
    for pattern in log_patterns:
        for file_path in glob.glob(pattern):
            try:
                file_stat = os.stat(file_path)
                file_mtime = file_stat.st_mtime
                file_size = file_stat.st_size
                file_date = datetime.fromtimestamp(file_mtime)
                
                if file_mtime < cutoff_time:
                    files_to_delete.append({
                        'path': file_path,
                        'size': file_size,
                        'date': file_date
                    })
                    total_size += file_size
                else:
                    kept_files += 1
                    kept_size += file_size
                    
            except OSError as e:
                print(f"无法访问文件 {file_path}: {e}")
    
    # 显示统计信息
    print(f"扫描结果:")
    print(f"  待删除文件: {len(files_to_delete)} 个")
    print(f"  待删除大小: {format_size(total_size)}")
    print(f"  保留文件: {kept_files} 个")
    print(f"  保留大小: {format_size(kept_size)}")
    print()
    
    if not files_to_delete:
        print("✅ 没有需要清理的日志文件")
        return
    
    # 显示待删除的文件
    print("待删除的文件:")
    for file_info in sorted(files_to_delete, key=lambda x: x['date']):
        print(f"  {file_info['date'].strftime('%Y-%m-%d %H:%M:%S')} - "
              f"{format_size(file_info['size'])} - {os.path.basename(file_info['path'])}")
    print()
    
    if dry_run:
        print("🔍 试运行模式 - 未实际删除文件")
        print("如需实际清理，请运行: python3 cleanup_logs.py --execute")
    else:
        # 实际删除文件
        deleted_count = 0
        deleted_size = 0
        
        for file_info in files_to_delete:
            try:
                os.remove(file_info['path'])
                deleted_count += 1
                deleted_size += file_info['size']
                print(f"✅ 已删除: {os.path.basename(file_info['path'])}")
            except OSError as e:
                print(f"❌ 删除失败 {file_info['path']}: {e}")
        
        print(f"\n清理完成:")
        print(f"  实际删除: {deleted_count} 个文件")
        print(f"  释放空间: {format_size(deleted_size)}")

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def analyze_log_directory():
    """分析日志目录状况"""
    log_dir = "./logs"
    
    print("日志目录分析")
    print("=" * 30)
    
    if not os.path.exists(log_dir):
        print(f"日志目录不存在: {log_dir}")
        return
    
    # 统计不同时间段的文件
    now = time.time()
    time_ranges = {
        "今天": 1,
        "3天内": 3,
        "7天内": 7,
        "30天内": 30,
        "30天以上": float('inf')
    }
    
    stats = {range_name: {'count': 0, 'size': 0} for range_name in time_ranges}
    
    for file_path in glob.glob(os.path.join(log_dir, "*.log")):
        try:
            file_stat = os.stat(file_path)
            file_age_days = (now - file_stat.st_mtime) / (24 * 60 * 60)
            file_size = file_stat.st_size
            
            for range_name, days in time_ranges.items():
                if file_age_days <= days:
                    stats[range_name]['count'] += 1
                    stats[range_name]['size'] += file_size
                    break
            
        except OSError:
            continue
    
    print("文件分布统计:")
    for range_name, data in stats.items():
        if data['count'] > 0:
            print(f"  {range_name}: {data['count']} 个文件, {format_size(data['size'])}")
    
    print()
    
    # 建议清理策略
    total_old_files = stats["30天以上"]['count']
    total_old_size = stats["30天以上"]['size']
    
    if total_old_files > 0:
        print(f"💡 建议清理 30天以上的 {total_old_files} 个文件，可释放 {format_size(total_old_size)} 空间")
    else:
        print("✅ 日志文件状态良好，无需清理")

def main():
    """主函数"""
    import sys
    
    # 先分析日志目录
    analyze_log_directory()
    print()
    
    # 检查命令行参数
    execute_mode = "--execute" in sys.argv or "-e" in sys.argv
    
    # 执行清理（默认保留7天）
    cleanup_logs(days_to_keep=7, dry_run=not execute_mode)

if __name__ == "__main__":
    main()