#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway部署测试脚本
用于验证Railway部署后的系统功能
"""

import requests
import json
import time
from datetime import datetime
import sys

class RailwayDeploymentTester:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_health_check(self):
        """测试健康检查接口"""
        print("\n🔍 测试健康检查接口...")
        try:
            response = self.session.get(f"{self.api_base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过")
                print(f"   状态: {data.get('status')}")
                print(f"   时间: {data.get('timestamp')}")
                print(f"   MongoDB: {data.get('mongodb_status')}")
                return True
            else:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_today_data(self):
        """测试今日数据接口"""
        print("\n🔍 测试今日数据接口...")
        try:
            response = self.session.get(f"{self.api_base_url}/api/today-data")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    records = data.get('data', [])
                    print(f"✅ 今日数据获取成功")
                    print(f"   记录数量: {len(records)}")
                    print(f"   查询时间: {data.get('query_time')}")
                    if records:
                        latest = records[0]
                        print(f"   最新期号: {latest.get('issue')}")
                        print(f"   开奖时间: {latest.get('time')}")
                    return True
                else:
                    print(f"❌ 今日数据获取失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 今日数据接口失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 今日数据接口异常: {e}")
            return False
    
    def test_latest_data(self):
        """测试最新数据接口"""
        print("\n🔍 测试最新数据接口...")
        try:
            response = self.session.get(f"{self.api_base_url}/api/latest-data")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    latest_record = data.get('data')
                    print(f"✅ 最新数据获取成功")
                    print(f"   期号: {latest_record.get('issue')}")
                    print(f"   开奖时间: {latest_record.get('time')}")
                    print(f"   开奖号码: {latest_record.get('numbers')}")
                    print(f"   查询时间: {data.get('query_time')}")
                    return True
                else:
                    print(f"❌ 最新数据获取失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 最新数据接口失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 最新数据接口异常: {e}")
            return False
    
    def test_cors(self):
        """测试CORS配置"""
        print("\n🔍 测试CORS配置...")
        try:
            # 发送OPTIONS预检请求
            headers = {
                'Origin': 'https://example.com',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            response = self.session.options(f"{self.api_base_url}/api/health", headers=headers)
            
            if response.status_code == 200:
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                }
                print(f"✅ CORS配置正确")
                for key, value in cors_headers.items():
                    if value:
                        print(f"   {key}: {value}")
                return True
            else:
                print(f"❌ CORS预检失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ CORS测试异常: {e}")
            return False
    
    def test_response_time(self):
        """测试响应时间"""
        print("\n🔍 测试API响应时间...")
        endpoints = [
            '/api/health',
            '/api/today-data',
            '/api/latest-data'
        ]
        
        results = []
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.api_base_url}{endpoint}")
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                results.append({
                    'endpoint': endpoint,
                    'response_time': response_time,
                    'status_code': response.status_code
                })
                
                status = "✅" if response.status_code == 200 and response_time < 5000 else "⚠️"
                print(f"   {status} {endpoint}: {response_time:.0f}ms (HTTP {response.status_code})")
                
            except Exception as e:
                print(f"   ❌ {endpoint}: 测试失败 - {e}")
                results.append({
                    'endpoint': endpoint,
                    'response_time': None,
                    'error': str(e)
                })
        
        avg_time = sum(r['response_time'] for r in results if r.get('response_time')) / len([r for r in results if r.get('response_time')])
        print(f"\n   平均响应时间: {avg_time:.0f}ms")
        
        return all(r.get('response_time', 0) < 5000 for r in results)
    
    def run_all_tests(self):
        """运行所有测试"""
        print(f"🚀 开始测试Railway部署: {self.api_base_url}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        tests = [
            ('健康检查', self.test_health_check),
            ('今日数据', self.test_today_data),
            ('最新数据', self.test_latest_data),
            ('CORS配置', self.test_cors),
            ('响应时间', self.test_response_time)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name}测试异常: {e}")
                results.append((test_name, False))
        
        # 测试总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结:")
        
        passed = 0
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        total = len(results)
        success_rate = (passed / total) * 100
        
        print(f"\n总体结果: {passed}/{total} 测试通过 ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 Railway部署测试基本通过！")
            return True
        else:
            print("⚠️ Railway部署存在问题，请检查日志和配置")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Railway部署测试脚本')
    parser.add_argument('api_url', help='Railway部署的API地址 (例如: https://your-app.railway.app)')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建测试器实例
    tester = RailwayDeploymentTester(args.api_url)
    
    # 运行测试
    success = tester.run_all_tests()
    
    # 退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()