import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests, hashlib, urllib.parse
from collections import OrderedDict

# 新商户配置
shop_id = "31442"
shop_token = "86eDkUqXgRuvlxsEzGH1O3cYLt4w7Zan"

print('=' * 70)
print('测试新商户 API')
print('=' * 70)
print(f'App ID: {shop_id}')
print(f'密钥: {shop_token}')
print('=' * 70)

# 测试 1: 查询余额
print('\n📋 测试 1: 查询余额')
data1 = {'id': shop_id}
data1 = OrderedDict(sorted(data1.items()))
query1 = urllib.parse.unquote(urllib.parse.urlencode(data1, quote_via=urllib.parse.quote))
sign_str1 = query1 + '&token=' + shop_token
data1['sign'] = hashlib.md5(sign_str1.encode()).hexdigest().upper()

print(f'请求数据: {dict(data1)}')
response1 = requests.post('https://api.okaypay.me/shop/balance', data=data1, timeout=10)
result1 = response1.json()
print(f'响应: {result1}')

if result1.get('status') == 'success':
    print('✅ 余额查询成功！')
    print(f'USDT: {result1["data"].get("usdt")}')
    print(f'TRX: {result1["data"].get("trx")}')
    print(f'CNY: {result1["data"].get("cny")}')
else:
    print(f'❌ 失败: {result1.get("msg")}')

# 测试 2: 创建支付链接
print('\n📋 测试 2: 创建支付链接')
data2 = {
    'amount': '1',
    'coin': 'USDT',
    'return_url': 'https://t.me/TGaccbbbot',
    'name': '测试订单',
    'unique_id': 'TEST_NEW_MERCHANT_001',
    'id': shop_id
}
data2 = OrderedDict(sorted(data2.items()))
query2 = urllib.parse.unquote(urllib.parse.urlencode(data2, quote_via=urllib.parse.quote))
sign_str2 = query2 + '&token=' + shop_token
data2['sign'] = hashlib.md5(sign_str2.encode()).hexdigest().upper()

print(f'请求数据: {dict(data2)}')
response2 = requests.post('https://api.okaypay.me/shop/payLink', data=data2, timeout=10)
result2 = response2.json()
print(f'响应: {result2}')

if result2.get('status') == 'success':
    print('\n🎉🎉🎉 支付链接创建成功！🎉🎉🎉')
    print(f'订单号: {result2["data"]["order_id"]}')
    print(f'支付链接: {result2["data"]["pay_url"]}')
    print('\n✅ 新商户 API 可用！')
else:
    print(f'\n❌ 失败: {result2.get("msg")}')

print('\n' + '=' * 70)
