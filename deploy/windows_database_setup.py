#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows本地部署 - 数据库配置脚本
支持SQLite、MySQL、PostgreSQL
"""

import sqlite3
import os
import json
from datetime import datetime

class DatabaseSetup:
    def __init__(self, db_type='sqlite'):
        self.db_type = db_type
        self.config = self.load_config()
    
    def load_config(self):
        """加载数据库配置"""
        config = {
            'sqlite': {
                'database': 'data/taiwan_pk10.db'
            },
            'mysql': {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': 'your_password',
                'database': 'taiwan_pk10'
            },
            'postgresql': {
                'host': 'localhost',
                'port': 5432,
                'user': 'postgres',
                'password': 'your_password',
                'database': 'taiwan_pk10'
            }
        }
        return config[self.db_type]
    
    def create_sqlite_database(self):
        """创建SQLite数据库和表结构"""
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(self.config['database'])
        cursor = conn.cursor()
        
        # 创建主数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS taiwan_pk10_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period VARCHAR(20) UNIQUE NOT NULL,
                numbers TEXT NOT NULL,
                draw_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_period ON taiwan_pk10_data(period)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_draw_time ON taiwan_pk10_data(draw_time)')
        
        conn.commit()
        conn.close()
        
        print(f"✅ SQLite数据库创建成功: {self.config['database']}")
        return True
    
    def create_mysql_database(self):
        """创建MySQL数据库和表结构"""
        try:
            import mysql.connector
            
            # 连接MySQL服务器
            conn = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password']
            )
            cursor = conn.cursor()
            
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {self.config['database']}")
            
            # 创建主数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS taiwan_pk10_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    period VARCHAR(20) UNIQUE NOT NULL,
                    numbers TEXT NOT NULL,
                    draw_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_period (period),
                    INDEX idx_draw_time (draw_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            conn.commit()
            conn.close()
            
            print(f"✅ MySQL数据库创建成功: {self.config['database']}")
            return True
            
        except ImportError:
            print("❌ 请先安装MySQL连接器: pip install mysql-connector-python")
            return False
        except Exception as e:
            print(f"❌ MySQL数据库创建失败: {e}")
            return False
    
    def create_postgresql_database(self):
        """创建PostgreSQL数据库和表结构"""
        try:
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            # 连接PostgreSQL服务器
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # 创建数据库
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.config['database']}'")
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.config['database']}")
            
            conn.close()
            
            # 连接到新数据库
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            cursor = conn.cursor()
            
            # 创建主数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS taiwan_pk10_data (
                    id SERIAL PRIMARY KEY,
                    period VARCHAR(20) UNIQUE NOT NULL,
                    numbers TEXT NOT NULL,
                    draw_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_period ON taiwan_pk10_data(period)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_draw_time ON taiwan_pk10_data(draw_time)')
            
            conn.commit()
            conn.close()
            
            print(f"✅ PostgreSQL数据库创建成功: {self.config['database']}")
            return True
            
        except ImportError:
            print("❌ 请先安装PostgreSQL连接器: pip install psycopg2")
            return False
        except Exception as e:
            print(f"❌ PostgreSQL数据库创建失败: {e}")
            return False
    
    def setup_database(self):
        """根据类型设置数据库"""
        print(f"🚀 开始设置 {self.db_type.upper()} 数据库...")
        
        if self.db_type == 'sqlite':
            return self.create_sqlite_database()
        elif self.db_type == 'mysql':
            return self.create_mysql_database()
        elif self.db_type == 'postgresql':
            return self.create_postgresql_database()
        else:
            print(f"❌ 不支持的数据库类型: {self.db_type}")
            return False
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            if self.db_type == 'sqlite':
                conn = sqlite3.connect(self.config['database'])
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM taiwan_pk10_data")
                count = cursor.fetchone()[0]
                conn.close()
                print(f"✅ SQLite连接测试成功，当前数据条数: {count}")
                
            elif self.db_type == 'mysql':
                import mysql.connector
                conn = mysql.connector.connect(**self.config)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM taiwan_pk10_data")
                count = cursor.fetchone()[0]
                conn.close()
                print(f"✅ MySQL连接测试成功，当前数据条数: {count}")
                
            elif self.db_type == 'postgresql':
                import psycopg2
                conn = psycopg2.connect(**self.config)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM taiwan_pk10_data")
                count = cursor.fetchone()[0]
                conn.close()
                print(f"✅ PostgreSQL连接测试成功，当前数据条数: {count}")
                
            return True
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {e}")
            return False

def main():
    """主函数"""
    print("🎯 Windows本地部署 - 数据库配置向导")
    print("=" * 50)
    
    # 选择数据库类型
    print("请选择数据库类型:")
    print("1. SQLite (推荐，最简单)")
    print("2. MySQL")
    print("3. PostgreSQL")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    db_type_map = {
        '1': 'sqlite',
        '2': 'mysql', 
        '3': 'postgresql'
    }
    
    db_type = db_type_map.get(choice, 'sqlite')
    
    # 创建数据库设置实例
    db_setup = DatabaseSetup(db_type)
    
    # 设置数据库
    if db_setup.setup_database():
        # 测试连接
        if db_setup.test_connection():
            print("\n🎉 数据库配置完成！")
            print(f"数据库类型: {db_type.upper()}")
            if db_type == 'sqlite':
                print(f"数据库文件: {db_setup.config['database']}")
            else:
                print(f"数据库名称: {db_setup.config['database']}")
        else:
            print("\n❌ 数据库配置失败，请检查配置信息")
    else:
        print("\n❌ 数据库创建失败")

if __name__ == "__main__":
    main()