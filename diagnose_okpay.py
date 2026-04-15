"""
OKPay API 完整诊断
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
import urllib.parse
from collections import OrderedDict
import requests
import json

shop_id = "31439"
shop_token = "9VdfeDiGoUXRuv5ACE1MbFhL0tr47Za"

def sign(data):
    """签名函数"""
    data['id'] = shop_id
    data = {k: v for k, v in data.items() if v is not None and v != ''}
    data = OrderedDict(sorted(data.items()))
    query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
    query = urllib.parse.unquote(query)
    sign_str = query + '&token=' + shop_token
    data['sign'] = hashlib.md5(sign_str.encode()).hexdigest().upper()
    return data, query, sign_str

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('🔍 OKPay API 完整诊断')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'商户 ID: {shop_id}')
print(f'密钥长度: {len(shop_token)} 字符')
print(f'密钥: {shop_token}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

# 测试 1：查询余额（最简单的接口）
print('📋 测试 1: 查询余额（balance）')
print('-' * 40)
data1, query1, sign_str1 = sign({})
print(f'请求数据: {dict(data1)}')
print(f'查询字符串: {query1}')
print(f'签名字符串: {sign_str1}')
print(f'签名结果: {data1["sign"]}')

try:
    response1 = requests.post(
        'https://api.okaypay.me/shop/balance',
        data=data1,
        headers={'User-Agent': 'HTTP CLIENT'},
        timeout=10
    )
    print(f'HTTP 状态码: {response1.status_code}')
    print(f'响应头: {dict(response1.headers)}')
    print(f'响应内容: {response1.text}')
    result1 = response1.json()
    print(f'响应 JSON: {json.dumps(result1, ensure_ascii=False, indent=2)}')
except Exception as e:
    print(f'❌ 请求失败: {e}')

print('\n')

# 测试 2：创建支付链接
print('📋 测试 2: 创建支付链接（payLink）')
print('-' * 40)
data2, query2, sign_str2 = sign({
    'amount': '1',
    'coin': 'USDT'
})
print(f'请求数据: {dict(data2)}')
print(f'查询字符串: {query2}')
print(f'签名字符串: {sign_str2}')
print(f'签名结果: {data2["sign"]}')

try:
    response2 = requests.post(
        'https://api.okaypay.me/shop/payLink',
        data=data2,
        headers={'User-Agent': 'HTTP CLIENT'},
        timeout=10
    )
    print(f'HTTP 状态码: {response2.status_code}')
    print(f'响应头: {dict(response2.headers)}')
    print(f'响应内容: {response2.text}')
    result2 = response2.json()
    print(f'响应 JSON: {json.dumps(result2, ensure_ascii=False, indent=2)}')
except Exception as e:
    print(f'❌ 请求失败: {e}')

print('\n')

# 测试 3：验证文档示例签名
print('📋 测试 3: 验证文档示例签名')
print('-' * 40)
doc_data = OrderedDict([
    ('amount', '10'),
    ('callback_url', 'http://127.0.0.1/callback'),
    ('coin', 'USDT'),
    ('id', '1'),
    ('name', 'test'),
    ('return_url', 'http://127.0.0.1'),
    ('unique_id', '123456')
])
doc_token = '123456'
doc_query = urllib.parse.unquote(urllib.parse.urlencode(doc_data, quote_via=urllib.parse.quote))
doc_sign_str = doc_query + '&token=' + doc_token
doc_sign = hashlib.md5(doc_sign_str.encode()).hexdigest().upper()

print(f'文档示例数据: {dict(doc_data)}')
print(f'查询字符串: {doc_query}')
print(f'签名字符串: {doc_sign_str}')
print(f'计算签名: {doc_sign}')
print(f'文档签名: 7465C8F4ED1BA0C8C2DB88E792374A65')
print(f'签名一致: {doc_sign == "7465C8F4ED1BA0C8C2DB88E792374A65"}')

print('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('诊断完成')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
