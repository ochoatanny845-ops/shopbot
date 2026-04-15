import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import hashlib
import urllib.parse
from collections import OrderedDict

print('=' * 70)
print('验证签名算法是否和文档一致')
print('=' * 70)

# 文档示例 1: payLink
print('\n📋 文档示例 1: payLink')
doc1_data = OrderedDict([
    ('amount', '10'),
    ('callback_url', 'http://127.0.0.1/callback'),
    ('coin', 'USDT'),
    ('id', '1'),
    ('name', 'test'),
    ('return_url', 'http://127.0.0.1'),
    ('unique_id', '123456')
])
doc1_token = '123456'
doc1_query = urllib.parse.unquote(urllib.parse.urlencode(doc1_data, quote_via=urllib.parse.quote))
doc1_sign_str = doc1_query + '&token=' + doc1_token
doc1_sign = hashlib.md5(doc1_sign_str.encode()).hexdigest().upper()

print(f'查询字符串: {doc1_query}')
print(f'签名字符串: {doc1_sign_str}')
print(f'计算签名: {doc1_sign}')
print(f'文档签名: 7465C8F4ED1BA0C8C2DB88E792374A65')
print(f'✅ 一致!' if doc1_sign == '7465C8F4ED1BA0C8C2DB88E792374A65' else '❌ 不一致!')

# 文档示例 2: transfer
print('\n📋 文档示例 2: transfer')
doc2_data = OrderedDict([
    ('amount', '10'),
    ('callback_url', 'http://127.0.0.1/callback'),
    ('coin', 'USDT'),
    ('id', '1'),
    ('name', 'test'),
    ('to_user_id', '123456'),
    ('unique_id', '123456')
])
doc2_token = '123456'
doc2_query = urllib.parse.unquote(urllib.parse.urlencode(doc2_data, quote_via=urllib.parse.quote))
doc2_sign_str = doc2_query + '&token=' + doc2_token
doc2_sign = hashlib.md5(doc2_sign_str.encode()).hexdigest().upper()

print(f'查询字符串: {doc2_query}')
print(f'签名字符串: {doc2_sign_str}')
print(f'计算签名: {doc2_sign}')
print(f'文档签名: 09BC57D2B2AAFAA59DC56E82B8F79E03')
print(f'✅ 一致!' if doc2_sign == '09BC57D2B2AAFAA59DC56E82B8F79E03' else '❌ 不一致!')

# 测试我们的实际请求
print('\n' + '=' * 70)
print('测试实际请求（你的商户配置）')
print('=' * 70)

shop_id = '31439'
shop_token = '9VdfeDiGoUXRuv5ACE1MbFhL0tr47Za'

# balance 接口
print('\n📋 balance 接口')
balance_data = OrderedDict([('id', shop_id)])
balance_query = urllib.parse.unquote(urllib.parse.urlencode(balance_data, quote_via=urllib.parse.quote))
balance_sign_str = balance_query + '&token=' + shop_token
balance_sign = hashlib.md5(balance_sign_str.encode()).hexdigest().upper()

print(f'查询字符串: {balance_query}')
print(f'签名字符串: {balance_sign_str}')
print(f'签名: {balance_sign}')
print(f'请求数据: {{"id": "{shop_id}", "sign": "{balance_sign}"}}')

# 实际请求
import requests
balance_req_data = {'id': shop_id, 'sign': balance_sign}
print('\n发送请求到 OKPay...')
response = requests.post('https://api.okaypay.me/shop/balance', data=balance_req_data, timeout=10)
print(f'响应: {response.json()}')

# payLink 接口
print('\n📋 payLink 接口')
paylink_data = OrderedDict([
    ('amount', '1'),
    ('coin', 'USDT'),
    ('id', shop_id)
])
paylink_query = urllib.parse.unquote(urllib.parse.urlencode(paylink_data, quote_via=urllib.parse.quote))
paylink_sign_str = paylink_query + '&token=' + shop_token
paylink_sign = hashlib.md5(paylink_sign_str.encode()).hexdigest().upper()

print(f'查询字符串: {paylink_query}')
print(f'签名字符串: {paylink_sign_str}')
print(f'签名: {paylink_sign}')

paylink_req_data = {'amount': '1', 'coin': 'USDT', 'id': shop_id, 'sign': paylink_sign}
print('\n发送请求到 OKPay...')
response2 = requests.post('https://api.okaypay.me/shop/payLink', data=paylink_req_data, timeout=10)
print(f'响应: {response2.json()}')

print('\n' + '=' * 70)
print('诊断完成')
print('=' * 70)
