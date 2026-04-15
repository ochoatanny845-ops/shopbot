"""
验证签名逻辑是否和文档一致
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
import urllib.parse
from collections import OrderedDict

# 文档中的示例
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('📋 文档示例验证')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

# 文档示例数据
doc_data = {
    'amount': '10',
    'callback_url': 'http://127.0.0.1/callback',
    'coin': 'USDT',
    'id': '1',
    'name': 'test',
    'return_url': 'http://127.0.0.1',
    'unique_id': '123456'
}

doc_token = '123456'

# 排序
doc_data_sorted = OrderedDict(sorted(doc_data.items()))

# 生成查询字符串
query = urllib.parse.urlencode(doc_data_sorted, quote_via=urllib.parse.quote)
query = urllib.parse.unquote(query)

print(f'数据: {doc_data_sorted}')
print(f'查询字符串: {query}')
print(f'签名字符串: {query}&token={doc_token}')

# 签名
sign = hashlib.md5((query + '&token=' + doc_token).encode()).hexdigest().upper()

print(f'计算签名: {sign}')
print(f'文档签名: 7465C8F4ED1BA0C8C2DB88E792374A65')
print(f'是否一致: {sign == "7465C8F4ED1BA0C8C2DB88E792374A65"}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
