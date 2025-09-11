#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置真实的MongoDB Atlas连接
为用户提供配置选项和测试连接
"""

import os
from pymongo import MongoClient
from datetime import datetime
import json

def test_mongodb_connection(uri, db_name):
    """测试MongoDB连接"""
    try:
        print(f"正在测试连接: {uri[:50]}...")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB连接成功！")
        
        # 测试数据库访问
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"✅ 数据库 '{db_name}' 访问成功！")
        print(f"现有集合: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

def create_sample_data(uri, db_name):
    """创建示例数据"""
    try:
        client = MongoClient(uri)
        db = client[db_name]
        
        # 创建今日数据集合
        today_collection = db['today_data']
        today = datetime.now().strftime('%Y-%m-%d')
        
        today_data = {
            'date': today,
            'last_updated': datetime.now().isoformat(),
            'periods': [
                {
                    'period': '202501101',
                    'time': '09:10',
                    'numbers': [3, 7, 1, 9, 5, 2, 8, 4, 6, 10],
                    'draw_time': f'{today} 09:10:00'
                },
                {
                    'period': '202501102',
                    'time': '09:30',
                    'numbers': [8, 2, 5, 1, 9, 7, 3, 6, 4, 10],
                    'draw_time': f'{today} 09:30:00'
                }
            ]
        }
        
        # 插入或更新今日数据
        today_collection.replace_one(
            {'date': today},
            today_data,
            upsert=True
        )
        print(f"✅ 今日数据已同步到集合 'today_data'")
        
        # 创建历史数据集合
        history_collection = db['taiwan_pk10_data']
        
        history_data = [
            {
                'date': '2025-01-09',
                'periods': [
                    {
                        'period': '202501091',
                        'time': '09:10',
                        'numbers': [1, 5, 8, 3, 9, 2, 7, 4, 6, 10],
                        'draw_time': '2025-01-09 09:10:00'
                    },
                    {
                        'period': '202501092',
                        'time': '09:30',
                        'numbers': [6, 2, 9, 1, 4, 8, 5, 3, 7, 10],
                        'draw_time': '2025-01-09 09:30:00'
                    }
                ],
                'total_periods': 2
            },
            {
                'date': '2025-01-08',
                'periods': [
                    {
                        'period': '202501081',
                        'time': '09:10',
                        'numbers': [4, 7, 2, 8, 1, 9, 3, 5, 6, 10],
                        'draw_time': '2025-01-08 09:10:00'
                    }
                ],
                'total_periods': 1
            }
        ]
        
        # 插入历史数据
        for data in history_data:
            history_collection.replace_one(
                {'date': data['date']},
                data,
                upsert=True
            )
        
        print(f"✅ 历史数据已同步到集合 'taiwan_pk10_data'")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据同步失败: {str(e)}")
        return False

def update_env_file(uri):
    """更新.env文件"""
    try:
        env_path = '.env'
        
        # 读取现有内容
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新MONGODB_URI
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('MONGODB_URI='):
                lines[i] = f'MONGODB_URI="{uri}"\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'MONGODB_URI="{uri}"\n')
        
        # 写回文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ .env文件已更新")
        return True
        
    except Exception as e:
        print(f"❌ 更新.env文件失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=== MongoDB Atlas 配置向导 ===")
    print("\n当前需要配置有效的MongoDB Atlas连接字符串")
    print("\n选项:")
    print("1. 使用免费的MongoDB Atlas演示集群 (推荐)")
    print("2. 输入您自己的MongoDB Atlas连接字符串")
    print("3. 跳过配置，使用现有设置")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == '1':
        # 使用免费演示集群
        demo_uri = "mongodb+srv://readonly:readonly@cluster0.e1q2w.mongodb.net/sample_mflix?retryWrites=true&w=majority"
        db_name = "taiwan_pk10"
        
        print("\n使用演示集群进行测试...")
        if test_mongodb_connection(demo_uri, "sample_mflix"):
            # 修改为我们的数据库
            our_uri = demo_uri.replace("sample_mflix", db_name)
            print(f"\n配置我们的数据库: {db_name}")
            
            if update_env_file(our_uri):
                print("\n正在创建示例数据...")
                if create_sample_data(our_uri, db_name):
                    print("\n🎉 配置完成！")
                    print("\n下一步:")
                    print("1. 重启API服务器")
                    print("2. 测试API端点")
                    print("3. 部署到Railway")
                else:
                    print("\n⚠️  数据同步失败，但连接配置已完成")
        
    elif choice == '2':
        uri = input("\n请输入您的MongoDB Atlas连接字符串: ").strip()
        db_name = input("请输入数据库名称 (默认: taiwan_pk10): ").strip() or "taiwan_pk10"
        
        if test_mongodb_connection(uri, db_name):
            if update_env_file(uri):
                print("\n正在创建示例数据...")
                if create_sample_data(uri, db_name):
                    print("\n🎉 配置完成！")
                else:
                    print("\n⚠️  数据同步失败，但连接配置已完成")
    
    elif choice == '3':
        print("\n跳过配置，使用现有设置")
    
    else:
        print("\n无效选择，退出")

if __name__ == "__main__":
    main()