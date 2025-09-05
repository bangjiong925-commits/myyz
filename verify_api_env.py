#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

print('=== 验证API服务器环境变量 ===')

# 1. 检查当前Python进程的环境变量
print('\n1. 当前Python进程环境变量:')
print(f'MONGODB_URI: {os.environ.get("MONGODB_URI", "未设置")}')

# 2. 模拟source .env && python的环境
print('\n2. 模拟API服务器启动环境:')
try:
    # 读取.env文件
    with open('.env', 'r') as f:
        env_content = f.read()
    print('✓ .env文件存在')
    
    # 解析.env文件中的MONGODB_URI
    for line in env_content.split('\n'):
        if line.startswith('MONGODB_URI=') and not line.startswith('#'):
            uri = line.split('=', 1)[1]
            print(f'✓ .env中的MONGODB_URI: {uri}')
            break
    else:
        print('✗ .env中未找到MONGODB_URI')
        
except Exception as e:
    print(f'✗ 读取.env文件失败: {e}')

# 3. 测试source .env的效果
print('\n3. 测试source .env的效果:')
try:
    result = subprocess.run(
        ['bash', '-c', 'source .env && echo "MONGODB_URI=$MONGODB_URI"'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f'✓ source .env结果: {result.stdout.strip()}')
    else:
        print(f'✗ source .env失败: {result.stderr}')
except Exception as e:
    print(f'✗ 测试source .env失败: {e}')

# 4. 分析API服务器的实际行为
print('\n=== 分析结论 ===')
print('API服务器启动命令: source .env && python3 api_server.py')
print('这意味着API服务器应该使用.env文件中的配置')
print('但代码中有硬编码的默认值，可能覆盖了环境变量')

# 5. 检查API服务器代码的默认值逻辑
print('\n5. API服务器连接逻辑分析:')
print('代码: self.mongo_uri = os.environ.get(\'MONGODB_URI\', \'mongodb+srv://a1234:a1234@cluster0.mongodb.net/\')')
print('如果环境变量MONGODB_URI存在，应该使用环境变量值')
print('如果不存在，才使用硬编码的云端连接')