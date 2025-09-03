#!/usr/bin/env python3
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['taiwan_pk10']
collection = db['lottery_data']

# 检查期号114049874-114049884范围内的记录
start_period = 114049874
end_period = 114049884

count = collection.count_documents({
    'period': {'$gte': start_period, '$lte': end_period}
})

print(f'期号{start_period}-{end_period}范围内的记录数: {count}')

# 获取这个范围内的所有记录
records = list(collection.find({
    'period': {'$gte': start_period, '$lte': end_period}
}).sort('period', 1))

print(f'实际查询到的记录数: {len(records)}')

if records:
    print('\n前10条记录:')
    for i, record in enumerate(records[:10]):
        print(f'  {i+1}. 期号: {record["period"]}, ID: {str(record["_id"])}')
    
    # 统计每个期号的记录数
    from collections import Counter
    period_counts = Counter([r['period'] for r in records])
    print(f'\n期号统计 (共{len(period_counts)}个不同期号):')
    for period in sorted(period_counts.keys()):
        print(f'  期号 {period}: {period_counts[period]} 条记录')
else:
    print('\n没有找到任何记录')
    
    # 检查最接近的记录
    print('\n检查最接近的记录:')
    before = list(collection.find({'period': {'$lt': start_period}}).sort('period', -1).limit(3))
    after = list(collection.find({'period': {'$gt': end_period}}).sort('period', 1).limit(3))
    
    print(f'小于{start_period}的最后3条:')
    for record in before:
        print(f'  期号: {record["period"]}')
    
    print(f'大于{end_period}的前3条:')
    for record in after:
        print(f'  期号: {record["period"]}')

client.close()