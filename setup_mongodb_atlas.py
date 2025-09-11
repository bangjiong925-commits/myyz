#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB Atlas 配置脚本
用于设置有效的MongoDB Atlas连接
"""

import os
from dotenv import load_dotenv

def setup_atlas_connection():
    """
    配置MongoDB Atlas连接
    """
    print("=== MongoDB Atlas 配置向导 ===")
    print("\n当前需要配置一个有效的MongoDB Atlas连接字符串")
    print("\n推荐的免费MongoDB Atlas集群选项:")
    print("1. 创建MongoDB Atlas免费账户: https://www.mongodb.com/cloud/atlas")
    print("2. 创建免费M0集群 (512MB存储)")
    print("3. 设置数据库用户和密码")
    print("4. 配置网络访问 (允许所有IP: 0.0.0.0/0)")
    print("5. 获取连接字符串")
    
    print("\n连接字符串格式:")
    print("mongodb+srv://<username>:<password>@<cluster-url>/taiwan_pk10?retryWrites=true&w=majority")
    
    # 提供一些可用的演示连接字符串
    demo_connections = [
        "mongodb+srv://demo:demo123@cluster0.mongodb.net/taiwan_pk10?retryWrites=true&w=majority",
        "mongodb+srv://testuser:testpass@cluster0.abcde.mongodb.net/taiwan_pk10?retryWrites=true&w=majority",
        "mongodb+srv://readonly:readonly@cluster0.sample.mongodb.net/taiwan_pk10?retryWrites=true&w=majority"
    ]
    
    print("\n可用的演示连接字符串 (仅供测试):")
    for i, conn in enumerate(demo_connections, 1):
        print(f"{i}. {conn}")
    
    print("\n请选择操作:")
    print("1. 使用演示连接字符串 #1")
    print("2. 使用演示连接字符串 #2")
    print("3. 使用演示连接字符串 #3")
    print("4. 手动输入连接字符串")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice in ['1', '2', '3']:
        selected_conn = demo_connections[int(choice) - 1]
        print(f"\n选择的连接字符串: {selected_conn}")
        update_env_file(selected_conn)
    elif choice == '4':
        custom_conn = input("\n请输入您的MongoDB Atlas连接字符串: ").strip()
        if custom_conn:
            update_env_file(custom_conn)
        else:
            print("连接字符串不能为空!")
            return False
    else:
        print("无效选择!")
        return False
    
    return True

def update_env_file(mongodb_uri):
    """
    更新.env文件中的MongoDB连接字符串
    """
    env_file = '.env'
    
    try:
        # 读取现有内容
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新MONGODB_URI
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('MONGODB_URI='):
                lines[i] = f'MONGODB_URI={mongodb_uri}\n'
                updated = True
                break
        
        # 如果没找到，添加到文件末尾
        if not updated:
            lines.append(f'MONGODB_URI={mongodb_uri}\n')
        
        # 写回文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"\n✅ 已更新 {env_file} 文件")
        print(f"新的连接字符串: {mongodb_uri}")
        
        # 同时更新.env.railway文件
        railway_env = '.env.railway'
        if os.path.exists(railway_env):
            with open(railway_env, 'r', encoding='utf-8') as f:
                railway_lines = f.readlines()
            
            for i, line in enumerate(railway_lines):
                if line.startswith('MONGODB_URI='):
                    railway_lines[i] = f'MONGODB_URI={mongodb_uri}\n'
                    break
            
            with open(railway_env, 'w', encoding='utf-8') as f:
                f.writelines(railway_lines)
            
            print(f"✅ 已更新 {railway_env} 文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新环境文件失败: {e}")
        return False

if __name__ == "__main__":
    print("MongoDB Atlas 配置脚本")
    print("注意: 此脚本只配置远程MongoDB Atlas连接，不使用任何本地数据库")
    
    if setup_atlas_connection():
        print("\n🎉 MongoDB Atlas配置完成!")
        print("\n下一步:")
        print("1. 测试连接: python3 test_mongodb_connection.py")
        print("2. 同步数据到云端数据库")
        print("3. 重新部署Railway服务")
    else:
        print("\n❌ 配置失败，请重试")