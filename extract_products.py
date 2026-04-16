#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取所有商品名并分析中文词汇
"""

import sqlite3
import re

# 连接数据库
conn = sqlite3.connect('shopbot.db')
c = conn.cursor()

# 获取所有商品名
c.execute('SELECT DISTINCT name FROM products WHERE is_active = 1 ORDER BY name')
products = c.fetchall()
conn.close()

# 保存到文件
with open('products_all.txt', 'w', encoding='utf-8') as f:
    for p in products:
        f.write(p[0] + '\n')

print(f'✅ 提取了 {len(products)} 个商品名')
print(f'✅ 已保存到 products_all.txt')

# 分析中文词汇
chinese_parts = set()
for p in products:
    name = p[0]
    # 提取所有中文字符串（连续的中文字符）
    matches = re.findall(r'[\u4e00-\u9fff~（）-]+', name)
    for match in matches:
        # 清理前后的符号
        cleaned = match.strip('~-（）')
        if cleaned:
            chinese_parts.add(cleaned)

print(f'\n📝 发现 {len(chinese_parts)} 个中文词汇：')
for word in sorted(chinese_parts, key=len, reverse=True):
    print(f'  {word}')
