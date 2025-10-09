#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB数据库初始化脚本
用于设置Vercel MongoDB数据库并导入现有数据
"""

import os
import sys
import json
import glob
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mongodb_manager import MongoDBManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_environment():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        
        # 尝试加载.env文件
        env_path = project_root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"已加载环境变量文件: {env_path}")
        else:
            logger.warning("未找到.env文件，请确保已设置环境变量")
        
        # 检查必要的环境变量
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            logger.error("未找到MONGODB_URI环境变量")
            return False
        
        logger.info("环境变量加载成功")
        return True
        
    except ImportError:
        logger.error("未安装python-dotenv，请运行: pip install python-dotenv")
        return False
    except Exception as e:
        logger.error(f"加载环境变量失败: {e}")
        return False

def find_existing_data_files():
    """查找现有的数据文件"""
    data_files = []
    
    # 查找data目录中的JSON文件
    data_dir = project_root / 'data'
    if data_dir.exists():
        json_files = list(data_dir.glob('*.json'))
        data_files.extend(json_files)
        logger.info(f"在data目录找到 {len(json_files)} 个JSON文件")
    
    # 查找其他可能的数据文件位置
    other_patterns = [
        project_root / '*.json',
        project_root / 'backup' / '*.json',
        project_root / 'exports' / '*.json'
    ]
    
    for pattern in other_patterns:
        files = list(pattern.parent.glob(pattern.name)) if pattern.parent.exists() else []
        data_files.extend(files)
    
    # 去重并排序
    data_files = sorted(list(set(data_files)))
    
    logger.info(f"总共找到 {len(data_files)} 个数据文件")
    return data_files

def parse_json_data(file_path):
    """解析JSON数据文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 如果是单个对象，转换为列表
        if isinstance(data, dict):
            data = [data]
        
        # 验证数据格式
        valid_data = []
        for item in data:
            if isinstance(item, dict) and 'issue' in item:
                # 确保必要字段存在
                if 'numbers' not in item:
                    item['numbers'] = []
                if 'date' not in item:
                    item['date'] = datetime.now().strftime('%Y-%m-%d')
                if 'time' not in item:
                    item['time'] = datetime.now().strftime('%H:%M:%S')
                if 'timestamp' not in item:
                    item['timestamp'] = datetime.now().isoformat()
                
                valid_data.append(item)
        
        logger.info(f"从 {file_path} 解析出 {len(valid_data)} 条有效数据")
        return valid_data
        
    except Exception as e:
        logger.error(f"解析文件 {file_path} 失败: {e}")
        return []

def import_data_to_mongodb(db_manager, data_files):
    """导入数据到MongoDB"""
    total_imported = 0
    
    for file_path in data_files:
        logger.info(f"正在处理文件: {file_path}")
        
        data = parse_json_data(file_path)
        if data:
            imported_count = db_manager.insert_batch_data(data)
            total_imported += imported_count
            logger.info(f"从 {file_path} 导入 {imported_count} 条数据")
        else:
            logger.warning(f"文件 {file_path} 没有有效数据")
    
    return total_imported

def create_sample_data():
    """创建示例数据"""
    sample_data = []
    
    # 创建一些示例数据
    for i in range(5):
        issue_num = f"20241201{str(i+1).zfill(3)}"
        sample_data.append({
            "issue": issue_num,
            "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "date": "2024-12-01",
            "time": f"10:{str(i*2).zfill(2)}:00",
            "timestamp": f"2024-12-01T10:{str(i*2).zfill(2)}:00.000Z"
        })
    
    return sample_data

def setup_mongodb():
    """设置MongoDB数据库"""
    logger.info("开始MongoDB数据库初始化...")
    
    # 1. 加载环境变量
    if not load_environment():
        logger.error("环境变量加载失败，无法继续")
        return False
    
    try:
        # 2. 创建数据库管理器
        with MongoDBManager() as db_manager:
            logger.info("MongoDB连接管理器创建成功")
            
            # 3. 测试连接
            if not db_manager.test_connection():
                logger.error("MongoDB连接测试失败")
                return False
            
            logger.info("✅ MongoDB连接测试成功")
            
            # 4. 获取当前数据库状态
            stats = db_manager.get_database_stats()
            logger.info(f"数据库当前状态:")
            logger.info(f"  - 数据库名: {stats.get('database_name')}")
            logger.info(f"  - 集合名: {stats.get('collection_name')}")
            logger.info(f"  - 现有文档数: {stats.get('total_documents')}")
            
            # 5. 查找现有数据文件
            data_files = find_existing_data_files()
            
            if data_files:
                # 6. 导入现有数据
                logger.info("开始导入现有数据...")
                imported_count = import_data_to_mongodb(db_manager, data_files)
                logger.info(f"✅ 数据导入完成，共导入 {imported_count} 条数据")
            else:
                # 7. 如果没有现有数据，创建示例数据
                logger.info("未找到现有数据文件，创建示例数据...")
                sample_data = create_sample_data()
                imported_count = db_manager.insert_batch_data(sample_data)
                logger.info(f"✅ 示例数据创建完成，共创建 {imported_count} 条数据")
            
            # 8. 获取最终统计信息
            final_stats = db_manager.get_database_stats()
            logger.info(f"数据库最终状态:")
            logger.info(f"  - 文档总数: {final_stats.get('total_documents')}")
            logger.info(f"  - 最新期号: {final_stats.get('latest_issue')}")
            logger.info(f"  - 最旧期号: {final_stats.get('oldest_issue')}")
            
            # 9. 创建备份
            backup_file = project_root / 'data' / f'mongodb_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            backup_file.parent.mkdir(exist_ok=True)
            
            if db_manager.backup_to_json(str(backup_file)):
                logger.info(f"✅ 数据备份完成: {backup_file}")
            
            logger.info("🎉 MongoDB数据库初始化完成！")
            return True
            
    except Exception as e:
        logger.error(f"MongoDB初始化失败: {e}")
        return False

def verify_setup():
    """验证设置是否成功"""
    logger.info("开始验证MongoDB设置...")
    
    try:
        with MongoDBManager() as db_manager:
            # 测试基本操作
            if not db_manager.test_connection():
                logger.error("❌ 连接验证失败")
                return False
            
            # 测试数据查询
            latest_data = db_manager.get_latest_data(limit=3)
            if latest_data:
                logger.info(f"✅ 数据查询验证成功，获取到 {len(latest_data)} 条数据")
                for i, data in enumerate(latest_data, 1):
                    logger.info(f"  {i}. 期号: {data.get('issue')}")
            else:
                logger.warning("⚠️ 数据查询返回空结果")
            
            # 测试数据插入
            test_data = {
                "issue": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": datetime.now().strftime('%H:%M:%S'),
                "timestamp": datetime.now().isoformat()
            }
            
            if db_manager.insert_data(test_data):
                logger.info("✅ 数据插入验证成功")
            else:
                logger.error("❌ 数据插入验证失败")
                return False
            
            logger.info("🎉 MongoDB设置验证完成！")
            return True
            
    except Exception as e:
        logger.error(f"验证过程失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("MongoDB数据库初始化脚本")
    print("=" * 60)
    
    try:
        # 检查依赖
        try:
            import pymongo
            import certifi
            logger.info("✅ 依赖检查通过")
        except ImportError as e:
            logger.error(f"❌ 缺少依赖: {e}")
            logger.error("请运行: pip install pymongo certifi python-dotenv")
            return False
        
        # 执行初始化
        if setup_mongodb():
            # 验证设置
            if verify_setup():
                print("\n" + "=" * 60)
                print("🎉 MongoDB数据库初始化和验证完成！")
                print("现在可以使用以下方式连接数据库：")
                print("1. 使用mongodb_manager.py中的MongoDBManager类")
                print("2. 启动API服务器进行数据操作")
                print("=" * 60)
                return True
            else:
                logger.error("❌ 设置验证失败")
                return False
        else:
            logger.error("❌ 数据库初始化失败")
            return False
            
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        return False
    except Exception as e:
        logger.error(f"初始化过程中出现未预期的错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)