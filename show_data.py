#!/usr/bin/env python3
import json

# 读取数据文件
with open('data/latest_taiwan_pk10_data.json', 'r') as f:
    data = json.load(f)

print(f"数据库统计信息:")
print(f"总记录数: {len(data)}")
print(f"最新记录期号: {data[0]['period']}")
print(f"最早记录期号: {data[-1]['period']}")
print(f"最新开奖时间: {data[0]['drawTime']}")
print(f"最早开奖时间: {data[-1]['drawTime']}")
print(f"数据源: {data[0]['dataSource']}")
print()

print("最新5条开奖记录:")
for i in range(min(5, len(data))):
    record = data[i]
    print(f"期号: {record['period']}, 开奖号码: {record['drawNumbers']}, 时间: {record['drawTime']}")

print()
print("最早5条开奖记录:")
for i in range(max(0, len(data)-5), len(data)):
    record = data[i]
    print(f"期号: {record['period']}, 开奖号码: {record['drawNumbers']}, 时间: {record['drawTime']}")