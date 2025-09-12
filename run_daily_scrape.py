#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行每日数据抓取 - 快速获取今天和昨天的数据
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

try:
    from daily_scraper import DailyScraper
except ImportError:
    print("错误: 无法导入daily_scraper模块")
    print("请确保daily_scraper.py文件在当前目录")
    sys.exit(1)

def main():
    """主函数"""
    print("🚀 启动每日数据抓取器")
    print("📅 目标: 获取今天和昨天的台湾PK10数据")
    print("=" * 60)
    
    # 从环境变量获取MongoDB连接信息
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.environ.get('MONGODB_DB_NAME', 'taiwan_pk10')
    
    print(f"🔗 MongoDB URI: {mongodb_uri[:50]}..." if len(mongodb_uri) > 50 else f"🔗 MongoDB URI: {mongodb_uri}")
    print(f"🗄️  数据库名称: {db_name}")
    print("=" * 60)
    
    try:
        # 创建抓取器实例
        scraper = DailyScraper(mongodb_uri=mongodb_uri, db_name=db_name)
        
        # 运行抓取任务
        print("⏳ 开始抓取数据...")
        data = scraper.run_with_retry(max_retries=3)
        
        if data:
            print(f"\n✅ 抓取成功！")
            print(f"📊 总计获得: {len(data)} 条数据")
            print(f"💾 数据已保存到MongoDB数据库: {db_name}")
            
            # 显示数据统计
            if len(data) > 0:
                print(f"\n📈 数据统计:")
                print(f"   期号范围: {data[-1].period} - {data[0].period}")
                print(f"   时间范围: {data[-1].draw_time} - {data[0].draw_time}")
                
                # 按日期分组统计
                from collections import defaultdict
                date_counts = defaultdict(int)
                for item in data:
                    date_str = item.draw_date.strftime('%Y-%m-%d')
                    date_counts[date_str] += 1
                
                print(f"\n📅 按日期统计:")
                for date_str, count in sorted(date_counts.items()):
                    print(f"   {date_str}: {count} 条记录")
            
            print(f"\n🎉 任务完成！数据已准备就绪。")
        else:
            print(f"\n❌ 抓取失败！")
            print(f"💡 建议检查网络连接和目标网站状态")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 发生错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()