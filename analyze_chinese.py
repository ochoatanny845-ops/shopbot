#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从商品名中提取所有中文词汇
"""

import re

# 读取商品名列表
with open('C:/Users/Administrator/.openclaw/media/inbound/products_all---a56ec1c3-03a8-4e7d-b0f6-3b28417ca8b3.txt', 'r', encoding='utf-8') as f:
    products = [line.strip() for line in f if line.strip()]

# 提取所有中文词汇
chinese_parts = set()
for name in products:
    # 提取连续的中文字符串（包括~符号）
    matches = re.findall(r'~([^~\n]+)', name)
    for match in matches:
        cleaned = match.strip()
        if cleaned and re.search(r'[\u4e00-\u9fff]', cleaned):
            chinese_parts.add(cleaned)

# 按长度降序排序
sorted_parts = sorted(chinese_parts, key=len, reverse=True)

print(f'发现 {len(sorted_parts)} 个中文描述：\n')
for part in sorted_parts:
    print(f'  {part}')
