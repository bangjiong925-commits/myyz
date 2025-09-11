#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站可访问性测试脚本
测试目标网站: https://xn--kpro5poukl1g.com/#/
"""

import requests
import socket
import time
import urllib.parse
from datetime import datetime

def test_dns_resolution(domain):
    """测试DNS解析"""
    print("\n=== DNS解析测试 ===")
    try:
        # 解析域名
        ip_address = socket.gethostbyname(domain)
        print(f"✓ DNS解析成功: {domain} -> {ip_address}")
        return True, ip_address
    except socket.gaierror as e:
        print(f"✗ DNS解析失败: {e}")
        return False, None

def test_website_connection(url, timeout=10):
    """测试网站连接"""
    print(f"\n=== 网站连接测试 ===")
    print(f"测试URL: {url}")
    
    # 不同的User-Agent进行测试
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]
    
    results = []
    
    for i, ua in enumerate(user_agents, 1):
        print(f"\n--- 测试 {i}: User-Agent {i} ---")
        try:
            headers = {
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            end_time = time.time()
            
            response_time = round((end_time - start_time) * 1000, 2)
            
            result = {
                'user_agent_index': i,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'content_length': len(response.content),
                'final_url': response.url,
                'headers': dict(response.headers),
                'success': True
            }
            
            print(f"✓ 连接成功")
            print(f"  状态码: {response.status_code}")
            print(f"  响应时间: {response_time}ms")
            print(f"  内容长度: {len(response.content)} bytes")
            print(f"  最终URL: {response.url}")
            
            if response.status_code != 200:
                print(f"  ⚠️ 警告: 状态码不是200")
                
        except requests.exceptions.Timeout:
            result = {
                'user_agent_index': i,
                'error': 'Timeout',
                'success': False
            }
            print(f"✗ 连接超时 (>{timeout}秒)")
            
        except requests.exceptions.ConnectionError as e:
            result = {
                'user_agent_index': i,
                'error': f'ConnectionError: {str(e)}',
                'success': False
            }
            print(f"✗ 连接错误: {e}")
            
        except requests.exceptions.RequestException as e:
            result = {
                'user_agent_index': i,
                'error': f'RequestException: {str(e)}',
                'success': False
            }
            print(f"✗ 请求异常: {e}")
            
        results.append(result)
        time.sleep(1)  # 避免请求过于频繁
    
    return results

def test_different_methods(url):
    """测试不同的HTTP方法"""
    print(f"\n=== HTTP方法测试 ===")
    
    methods = ['HEAD', 'OPTIONS']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for method in methods:
        try:
            print(f"\n--- {method} 请求 ---")
            response = requests.request(method, url, headers=headers, timeout=10)
            print(f"✓ {method} 成功: 状态码 {response.status_code}")
            if response.headers:
                print(f"  服务器: {response.headers.get('Server', 'Unknown')}")
                print(f"  内容类型: {response.headers.get('Content-Type', 'Unknown')}")
        except Exception as e:
            print(f"✗ {method} 失败: {e}")

def analyze_results(results, domain):
    """分析测试结果"""
    print(f"\n=== 测试结果分析 ===")
    
    successful_tests = [r for r in results if r.get('success', False)]
    failed_tests = [r for r in results if not r.get('success', False)]
    
    print(f"成功测试: {len(successful_tests)}/{len(results)}")
    print(f"失败测试: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_response_time = sum(r['response_time_ms'] for r in successful_tests) / len(successful_tests)
        print(f"平均响应时间: {avg_response_time:.2f}ms")
        
        status_codes = [r['status_code'] for r in successful_tests]
        print(f"状态码分布: {set(status_codes)}")
    
    if failed_tests:
        print(f"\n失败原因分析:")
        error_types = {}
        for test in failed_tests:
            error = test.get('error', 'Unknown')
            error_type = error.split(':')[0]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            print(f"  {error_type}: {count}次")
    
    # 提供建议
    print(f"\n=== 建议和解决方案 ===")
    
    if len(failed_tests) == len(results):
        print("🔴 所有测试都失败了，可能的原因:")
        print("  1. 网站服务器宕机")
        print("  2. 域名DNS解析问题")
        print("  3. 网络连接问题")
        print("  4. IP被封禁")
        print("  5. 地区访问限制")
        print("  6. 防火墙或代理阻止")
        
        print("\n建议解决方案:")
        print("  1. 检查网络连接")
        print("  2. 尝试使用VPN")
        print("  3. 更换DNS服务器 (如8.8.8.8)")
        print("  4. 联系网站管理员")
        print("  5. 等待一段时间后重试")
        
    elif len(successful_tests) < len(results):
        print("🟡 部分测试失败，可能存在:")
        print("  1. 间歇性连接问题")
        print("  2. 服务器负载过高")
        print("  3. 特定User-Agent被限制")
        
    else:
        print("🟢 所有测试都成功，网站可正常访问")

def main():
    """主函数"""
    target_url = "https://xn--kpro5poukl1g.com/#/"
    domain = "xn--kpro5poukl1g.com"
    
    print(f"网站可访问性测试报告")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标网站: {target_url}")
    print("=" * 50)
    
    # 1. DNS解析测试
    dns_success, ip = test_dns_resolution(domain)
    
    # 2. 网站连接测试
    if dns_success:
        results = test_website_connection(target_url)
        
        # 3. 不同HTTP方法测试
        test_different_methods(target_url)
        
        # 4. 结果分析
        analyze_results(results, domain)
    else:
        print("\n由于DNS解析失败，跳过后续测试")
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 更换DNS服务器")
        print("3. 检查域名是否正确")
        print("4. 使用VPN尝试")
    
    print("\n=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main()