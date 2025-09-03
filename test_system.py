#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本 - 验证整个自动化系统是否正常工作
"""

import requests
import json
import time
from datetime import datetime

def test_mongodb_api():
    """测试MongoDB API服务器"""
    print("\n=== 测试MongoDB API服务器 ===")
    
    base_url = "http://localhost:3002"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ 健康检查通过")
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到MongoDB API服务器: {e}")
        return False
    
    # 测试今日数据
    try:
        response = requests.get(f"{base_url}/api/today-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                print(f"✓ 今日数据获取成功: {len(data['data'])} 条记录")
                print(f"  最新期号: {data['data'][0] if data['data'] else 'N/A'}")
            else:
                print("✗ 今日数据为空")
        else:
            print(f"✗ 今日数据获取失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 今日数据请求失败: {e}")
    
    # 测试最新数据
    try:
        response = requests.get(f"{base_url}/api/latest-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                print(f"✓ 最新数据获取成功: {len(data['data'])} 条记录")
            else:
                print("✗ 最新数据为空")
        else:
            print(f"✗ 最新数据获取失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 最新数据请求失败: {e}")
    
    return True

def test_scraper_api():
    """测试爬虫API服务器"""
    print("\n=== 测试爬虫API服务器 ===")
    
    base_url = "http://localhost:3001"
    
    # 测试爬虫触发
    try:
        response = requests.post(f"{base_url}/api/scrape", 
                               json={"action": "scrape_data", "max_pages": 2},
                               timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ 爬虫API调用成功")
                if data.get('data'):
                    print(f"  抓取到 {len(data['data'])} 条数据")
            else:
                print(f"✗ 爬虫执行失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"✗ 爬虫API调用失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 爬虫API请求失败: {e}")

def test_web_frontend():
    """测试Web前端"""
    print("\n=== 测试Web前端 ===")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✓ Web前端可访问")
            if "台湾PK数据分析工具" in response.text:
                print("✓ 页面内容正常")
            else:
                print("✗ 页面内容异常")
        else:
            print(f"✗ Web前端访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ Web前端请求失败: {e}")

def test_mongodb_connection():
    """测试MongoDB连接"""
    print("\n=== 测试MongoDB连接 ===")
    
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        
        # 测试连接
        client.admin.command('ping')
        print("✓ MongoDB连接成功")
        
        # 检查数据库和集合
        db = client['taiwan_pk10']
        collections = db.list_collection_names()
        
        if 'lottery_data' in collections:
            count = db.lottery_data.count_documents({})
            print(f"✓ lottery_data集合存在，包含 {count} 条记录")
        else:
            print("✗ lottery_data集合不存在")
        
        if 'web_formatted_data' in collections:
            count = db.web_formatted_data.count_documents({})
            print(f"✓ web_formatted_data集合存在，包含 {count} 条记录")
            
            # 获取最新记录
            latest = db.web_formatted_data.find_one(sort=[('期号', -1)])
            if latest:
                print(f"  最新期号: {latest.get('期号', 'N/A')}")
                print(f"  开奖号码: {latest.get('开奖号码', 'N/A')}")
        else:
            print("✗ web_formatted_data集合不存在")
        
        client.close()
        return True
        
    except ImportError:
        print("✗ pymongo未安装，无法测试MongoDB连接")
        return False
    except Exception as e:
        print(f"✗ MongoDB连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Taiwan PK10 自动爬虫系统测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行所有测试
    tests = [
        ("MongoDB连接", test_mongodb_connection),
        ("MongoDB API服务器", test_mongodb_api),
        ("爬虫API服务器", test_scraper_api),
        ("Web前端", test_web_frontend)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name}测试出错: {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "=" * 50)
    print("测试总结:")
    
    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！系统运行正常。")
    else:
        print(f"\n⚠️  有 {len(results) - passed} 项测试失败，请检查相关服务。")
    
    # 提供使用建议
    print("\n使用建议:")
    print("1. 确保所有服务都在运行:")
    print("   - MongoDB: sudo systemctl start mongod")
    print("   - Web服务器: python3 -m http.server 3000")
    print("   - 爬虫API: python3 api_server.py --port 3001")
    print("   - MongoDB API: python3 mongodb_api.py")
    print("2. 访问 http://localhost:3000 查看Web界面")
    print("3. 查看日志文件了解详细信息")

if __name__ == '__main__':
    main()