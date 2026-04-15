"""
测试最简参数
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
import urllib.parse
from collections import OrderedDict
import requests

shop_id = "31439"
shop_token = "VdeDkTmGogXqRuylxvCGHKMbcFoLr4wZ"

def sign(data):
    data['id'] = shop_id
    data = {k: v for k, v in data.items() if v}
    data = OrderedDict(sorted(data.items()))
    query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
    query = urllib.parse.unquote(query)
    data['sign'] = hashlib.md5((query + '&token=' + shop_token).encode()).hexdigest().upper()
    return data

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('🧪 测试不同参数组合')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

# 测试 1：最简参数（只有必填项）
print('📋 测试 1：最简参数（amount + coin）')
data1 = {
    'amount': '1',
    'coin': 'USDT'
}
data1 = sign(data1)
print(f'参数: {data1}')
response1 = requests.post('https://api.okaypay.me/shop/payLink', data=data1)
print(f'响应: {response1.json()}\n')

# 测试 2：添加 unique_id
print('📋 测试 2：添加 unique_id')
data2 = {
    'amount': '1',
    'coin': 'USDT',
    'unique_id': 'TEST_002'
}
data2 = sign(data2)
print(f'参数: {data2}')
response2 = requests.post('https://api.okaypay.me/shop/payLink', data=data2)
print(f'响应: {response2.json()}\n')

# 测试 3：完整参数
print('📋 测试 3：完整参数')
data3 = {
    'amount': '1',
    'coin': 'USDT',
    'unique_id': 'TEST_003',
    'name': '测试订单',
    'return_url': 'https://t.me/TGaccbbbot'
}
data3 = sign(data3)
print(f'参数: {data3}')
response3 = requests.post('https://api.okaypay.me/shop/payLink', data=data3)
print(f'响应: {response3.json()}\n')

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
