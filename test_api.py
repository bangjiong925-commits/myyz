#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API端点测试脚本
测试远程MongoDB Atlas连接和数据访问
"""

import requests
import json
from datetime import datetime

def test_api_endpoint(url, endpoint_name):
    """测试API端点"""
    try:
        print(f"\n=== 测试 {endpoint_name} ===")
        print(f"请求URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            except json.JSONDecodeError:
                print(f"响应内容 (非JSON): {response.text}")
                return False
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"连接错误: 无法连接到 {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"超时错误: 请求 {url} 超时")
        return False
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("开始测试API端点...")
    print(f"测试时间: {datetime.now().isoformat()}")
    
    base_url = "http://localhost:8000"
    
    # 测试端点列表
    endpoints = [
        ("/health", "健康检查"),
        ("/api/today-data", "今日数据"),
        ("/api/taiwan-pk10-data", "台湾PK10数据")
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        success = test_api_endpoint(url, name)
        results.append((name, success))
    
    # 总结测试结果
    print("\n=== 测试结果总结 ===")
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    print(f"\n总计: {success_count}/{total_count} 个端点测试成功")
    
    if success_count == total_count:
        print("\n🎉 所有API端点测试通过！远程MongoDB Atlas连接正常。")
    else:
        print("\n⚠️  部分API端点测试失败，请检查服务器状态和数据库连接。")

if __name__ == "__main__":
    main()