#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
展示今天的台湾PK10数据
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import Counter

def load_latest_data():
    """加载最新的数据文件"""
    data_dir = Path('data')
    if not data_dir.exists():
        print("❌ 数据目录不存在")
        return None
    
    # 查找最新的数据文件
    json_files = list(data_dir.glob('taiwan_pk10_data_*.json'))
    if not json_files:
        print("❌ 未找到数据文件")
        return None
    
    # 按文件名排序，获取最新的文件
    latest_file = sorted(json_files)[-1]
    print(f"📁 读取数据文件: {latest_file.name}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ 读取数据文件失败: {str(e)}")
        return None

def analyze_data(data):
    """分析数据"""
    if not data:
        return
    
    print("\n" + "=" * 60)
    print("📊 今日台湾PK10数据统计")
    print("=" * 60)
    
    # 基本统计
    total_records = len(data)
    print(f"📈 总记录数: {total_records} 条")
    
    if total_records == 0:
        print("❌ 暂无数据")
        return
    
    # 时间范围
    times = [record['drawTime'] for record in data if 'drawTime' in record]
    if times:
        earliest_time = min(times)
        latest_time = max(times)
        print(f"⏰ 时间范围: {earliest_time} - {latest_time}")
    
    # 期号范围
    periods = [record['period'] for record in data if 'period' in record]
    if periods:
        earliest_period = min(periods)
        latest_period = max(periods)
        print(f"🎯 期号范围: {earliest_period} - {latest_period}")
    
    # 数字统计
    all_numbers = []
    for record in data:
        if 'drawNumbers' in record and isinstance(record['drawNumbers'], list):
            all_numbers.extend(record['drawNumbers'])
    
    if all_numbers:
        number_counter = Counter(all_numbers)
        print(f"\n🔢 数字出现统计 (共 {len(all_numbers)} 个数字):")
        for num in range(1, 11):
            count = number_counter.get(num, 0)
            percentage = (count / len(all_numbers)) * 100 if all_numbers else 0
            print(f"   数字 {num:2d}: {count:3d} 次 ({percentage:5.1f}%)")
        
        # 最热和最冷数字
        most_common = number_counter.most_common(3)
        least_common = number_counter.most_common()[:-4:-1]
        
        print(f"\n🔥 最热数字: {', '.join([f'{num}({count}次)' for num, count in most_common])}")
        print(f"❄️  最冷数字: {', '.join([f'{num}({count}次)' for num, count in least_common])}")
    
    print("\n" + "=" * 60)
    print("📋 最新10期开奖结果")
    print("=" * 60)
    
    # 显示最新10期结果
    recent_data = data[:10]  # 数据已按时间倒序排列
    
    print(f"{'期号':<12} {'时间':<8} {'开奖号码':<30} {'冠亚军':<8}")
    print("-" * 60)
    
    for record in recent_data:
        period = record.get('period', 'N/A')
        draw_time = record.get('drawTime', 'N/A')
        draw_numbers = record.get('drawNumbers', [])
        
        if isinstance(draw_numbers, list) and len(draw_numbers) >= 2:
            numbers_str = ' '.join([f'{num:2d}' for num in draw_numbers])
            champion_runner = f"{draw_numbers[0]},{draw_numbers[1]}"
        else:
            numbers_str = 'N/A'
            champion_runner = 'N/A'
        
        print(f"{period:<12} {draw_time:<8} {numbers_str:<30} {champion_runner:<8}")
    
    print("\n" + "=" * 60)
    print("💡 数据说明")
    print("=" * 60)
    print("• 数据来源: 实时爬取")
    print("• 更新时间: 每5分钟自动更新")
    print("• 开奖频率: 每5分钟一期")
    print("• 数字范围: 1-10")
    print("• 冠亚军: 前两位数字")
    
    # 数据新鲜度
    if data:
        latest_record = data[0]
        scraped_time = latest_record.get('scrapedAt', '')
        if scraped_time:
            try:
                scraped_dt = datetime.fromisoformat(scraped_time.replace('Z', '+00:00'))
                now = datetime.now()
                time_diff = now - scraped_dt.replace(tzinfo=None)
                minutes_ago = int(time_diff.total_seconds() / 60)
                print(f"\n🕐 数据更新: {minutes_ago} 分钟前")
            except:
                pass

def main():
    """主函数"""
    print("🎲 台湾PK10数据查看器")
    print(f"📅 查看日期: {datetime.now().strftime('%Y年%m月%d日')}")
    
    # 加载数据
    data = load_latest_data()
    
    if data:
        # 分析数据
        analyze_data(data)
    else:
        print("\n❌ 无法加载数据，请检查:")
        print("1. 数据文件是否存在")
        print("2. 爬虫是否正常运行")
        print("3. 网络连接是否正常")

if __name__ == "__main__":
    main()