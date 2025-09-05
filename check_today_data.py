#!/usr/bin/env python3
import json
import sys
import requests
from datetime import datetime

def check_today_data():
    try:
        # 获取API数据
        response = requests.get('https://twpk.up.railway.app/api/taiwan-pk10-data?limit=100')
        data = response.json()
        
        # 获取今天的日期
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"检查日期: {today}")
        print("=" * 50)
        
        # 筛选今天的数据
        today_data = [d for d in data if today in d['drawDate']]
        
        print(f"今天数据条数: {len(today_data)}")
        
        if data:
            print(f"最新期号: {data[0]['period']}")
            print(f"最新开奖时间: {data[0]['drawDate']} {data[0]['drawTime']}")
            print(f"数据抓取时间: {data[0]['scrapedAt']}")
        else:
            print("无数据")
            return
        
        print("\n今天的数据:")
        if today_data:
            for i, d in enumerate(today_data[:10]):
                print(f"{i+1}. 期号: {d['period']}, 时间: {d['drawTime']}, 开奖号码: {d['drawNumbers'][:3]}...")
        else:
            print("今天暂无数据")
        
        # 检查数据时间范围
        if len(data) > 0:
            earliest = data[-1]
            latest = data[0]
            print(f"\n数据时间范围:")
            print(f"最早: {earliest['drawDate']} {earliest['drawTime']} (期号: {earliest['period']})")
            print(f"最新: {latest['drawDate']} {latest['drawTime']} (期号: {latest['period']})")
        
        # 检查数据更新状态
        if today_data:
            latest_today = today_data[0]
            scrape_time = datetime.fromisoformat(latest_today['scrapedAt'].replace('Z', '+00:00'))
            now = datetime.now()
            time_diff = now - scrape_time.replace(tzinfo=None)
            print(f"\n数据更新状态:")
            print(f"最后更新: {time_diff.total_seconds()/60:.1f} 分钟前")
            if time_diff.total_seconds() > 3600:  # 超过1小时
                print("⚠️ 数据可能未及时更新")
            else:
                print("✅ 数据更新正常")
        
    except Exception as e:
        print(f"检查数据时出错: {e}")

if __name__ == "__main__":
    check_today_data()