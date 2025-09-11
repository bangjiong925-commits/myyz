#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今日数据统计报告
"""

import json
import os
from datetime import datetime
from pathlib import Path

def analyze_today_data():
    """分析今天的数据情况"""
    data_dir = Path('data')
    today_str = '20250909'  # 今天的日期
    
    print("=" * 60)
    print("📊 今日云端数据库数据统计报告")
    print("=" * 60)
    print(f"📅 检查日期: 2025-09-09")
    print(f"🕐 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 查找今天的数据文件
    today_files = list(data_dir.glob(f'taiwan_pk10_data_{today_str}_*.json'))
    
    if not today_files:
        print("❌ 今天没有找到任何数据文件")
        return
    
    print(f"📁 找到今天的数据文件数量: {len(today_files)}")
    
    # 获取最新的数据文件
    latest_file = max(today_files, key=lambda x: x.stat().st_mtime)
    print(f"📄 最新数据文件: {latest_file.name}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("❌ 数据文件为空")
            return
        
        print(f"📈 最新文件中的数据条数: {len(data)}")
        
        # 分析最新数据
        latest_record = data[0]
        print(f"🎯 最新期号: {latest_record['period']}")
        print(f"🕐 最新开奖时间: {latest_record['drawTime']}")
        print(f"🎲 最新开奖号码: {latest_record['drawNumbers'][:5]}...")
        print(f"📡 数据抓取时间: {latest_record['scrapedAt']}")
        
        # 统计今天的数据
        today_data = [d for d in data if '2025-09-09' in d['drawDate']]
        print(f"📊 今天的开奖期数: {len(today_data)}")
        
        if today_data:
            earliest_today = today_data[-1]
            latest_today = today_data[0]
            print(f"🌅 今天最早期号: {earliest_today['period']} ({earliest_today['drawTime']})")
            print(f"🌆 今天最新期号: {latest_today['period']} ({latest_today['drawTime']})")
        
        # 数据更新状态
        scrape_time = datetime.fromisoformat(latest_record['scrapedAt'].replace('Z', '+00:00'))
        now = datetime.now()
        time_diff = now - scrape_time.replace(tzinfo=None)
        minutes_ago = time_diff.total_seconds() / 60
        
        print()
        print("🔄 数据更新状态:")
        print(f"⏰ 最后更新: {minutes_ago:.1f} 分钟前")
        
        if minutes_ago < 10:
            print("✅ 数据更新非常及时")
        elif minutes_ago < 30:
            print("✅ 数据更新正常")
        elif minutes_ago < 60:
            print("⚠️ 数据更新稍有延迟")
        else:
            print("❌ 数据可能未及时更新")
        
        # 数据质量检查
        print()
        print("🔍 数据质量检查:")
        valid_count = sum(1 for d in data if d.get('isValid', False))
        print(f"✅ 有效数据: {valid_count}/{len(data)} ({valid_count/len(data)*100:.1f}%)")
        
        # 数据源统计
        sources = {}
        for d in data:
            source = d.get('dataSource', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"📡 数据源分布:")
        for source, count in sources.items():
            print(f"   {source}: {count} 条 ({count/len(data)*100:.1f}%)")
        
        print()
        print("📋 总结:")
        print(f"✅ 云端数据库今天有数据: 是")
        print(f"📊 今天开奖期数: {len(today_data)} 期")
        print(f"📈 总数据量: {len(data)} 条")
        print(f"🔄 数据更新状态: {'正常' if minutes_ago < 30 else '延迟'}")
        print(f"✅ 数据完整性: {'良好' if valid_count/len(data) > 0.95 else '一般'}")
        
    except Exception as e:
        print(f"❌ 分析数据时出错: {e}")

if __name__ == "__main__":
    analyze_today_data()