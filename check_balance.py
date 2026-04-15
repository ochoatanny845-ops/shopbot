"""Check OKPay Balance"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import hashlib
import urllib.parse
from collections import OrderedDict

shop_id = "31439"
shop_token = "9VdfeDiGoUXRuv5ACE1MbFhL0tr47Za"

# 准备数据
data = {'id': shop_id}
data = OrderedDict(sorted(data.items()))

# 生成查询字符串
query = urllib.parse.unquote(urllib.parse.urlencode(data, quote_via=urllib.parse.quote))

# 签名
sign_str = query + '&token=' + shop_token
data['sign'] = hashlib.md5(sign_str.encode()).hexdigest().upper()

print('=' * 50)
print('查询 OKPay 商户余额')
print('=' * 50)
print(f'商户 ID: {shop_id}')
print(f'请求 URL: https://api.okaypay.me/shop/balance')
print(f'请求参数: {dict(data)}')
print(f'签名字符串: {sign_str}')
print(f'签名: {data["sign"]}')
print('=' * 50)

# 发送请求
response = requests.post('https://api.okaypay.me/shop/balance', data=data)

print(f'\nHTTP 状态码: {response.status_code}')
print(f'响应内容: {response.text}')
print('=' * 50)

result = response.json()

if result.get('status') == 'success':
    print('\n✅ 查询成功！')
    print(f'USDT 余额: {result["data"].get("usdt", 0)}')
    print(f'TRX 余额: {result["data"].get("trx", 0)}')
    print(f'CNY 余额: {result["data"].get("cny", 0)}')
elif result.get('msg') == '未授权':
    print('\n❌ 查询失败：未授权')
    print('\n可能的原因:')
    print('1. 商户 ID 或密钥错误')
    print('2. 商户状态不正常')
    print('3. IP 未加入白名单')
    print('4. OKPay 平台问题')
else:
    print(f'\n❌ 查询失败: {result.get("msg")}')
