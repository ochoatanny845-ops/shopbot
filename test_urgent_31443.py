import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests, hashlib, urllib.parse
from collections import OrderedDict
import time

# 最新商户 31443
shop_id = "31443"
shop_token = "96feDimoURly5ABsEzHNObcWYtJw7an"

print('=' * 70)
print('🚀 紧急测试新商户 31443')
print('=' * 70)
print(f'App ID: {shop_id}')
print(f'密钥: {shop_token}')
print(f'创建时间: 2026-04-15 14:21:26')
print(f'当前时间: {time.strftime("%Y-%m-%d %H:%M:%S")}')
print('=' * 70)

# 测试 1: 查询余额
print('\n📋 测试 1: 查询余额')
data1 = {'id': shop_id}
data1 = OrderedDict(sorted(data1.items()))
query1 = urllib.parse.unquote(urllib.parse.urlencode(data1, quote_via=urllib.parse.quote))
sign_str1 = query1 + '&token=' + shop_token
data1['sign'] = hashlib.md5(sign_str1.encode()).hexdigest().upper()

response1 = requests.post('https://api.okaypay.me/shop/balance', data=data1, timeout=10)
result1 = response1.json()
print(f'响应: {result1}')

if result1.get('status') == 'success':
    print('✅ 成功！')
    print(f'USDT: {result1["data"].get("usdt")}')
elif result1.get('msg') == '未授权':
    print('❌ 未授权 - 需要设置 IP 白名单和回调地址')
else:
    print(f'❌ 失败: {result1.get("msg")}')

# 测试 2: 创建支付链接
print('\n📋 测试 2: 创建支付链接')
data2 = {
    'amount': '1',
    'coin': 'USDT',
    'return_url': 'https://t.me/TGaccbbbot',
    'name': '紧急测试',
    'unique_id': f'URGENT_TEST_{int(time.time())}',
    'id': shop_id
}
data2 = OrderedDict(sorted(data2.items()))
query2 = urllib.parse.unquote(urllib.parse.urlencode(data2, quote_via=urllib.parse.quote))
sign_str2 = query2 + '&token=' + shop_token
data2['sign'] = hashlib.md5(sign_str2.encode()).hexdigest().upper()

response2 = requests.post('https://api.okaypay.me/shop/payLink', data=data2, timeout=10)
result2 = response2.json()
print(f'响应: {result2}')

if result2.get('status') == 'success':
    print('\n🎉 支付链接创建成功！')
    print(f'订单号: {result2["data"]["order_id"]}')
    print(f'支付链接: {result2["data"]["pay_url"]}')
elif result2.get('msg') == '未授权':
    print('❌ 未授权 - 需要立即设置 IP 白名单和回调地址')
else:
    print(f'❌ 失败: {result2.get("msg")}')

print('\n' + '=' * 70)
print('结论:')
if result1.get('status') == 'success' or result2.get('status') == 'success':
    print('✅ 新商户刚创建时可用')
    print('⚠️  需要立即设置 IP 白名单和回调地址，否则几分钟后会被限制')
    print('\n立即设置:')
    print('1. IP 白名单: 188.137.245.150')
    print('2. 回调地址: http://188.137.245.150:8888/okpay/callback')
else:
    print('❌ 商户创建后立即就被限制了')
    print('说明: OKPay 现在要求商户创建时就必须设置 IP 白名单和回调地址')
print('=' * 70)
