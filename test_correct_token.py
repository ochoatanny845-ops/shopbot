"""
使用正确的密钥测试
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
import urllib.parse
from collections import OrderedDict
import requests

# ✅ 正确的配置（从截图中提取）
shop_id = "31439"
shop_token = "VdeDkTmGogXgRuvkyCGHKMbcFpLr4wZ"  # 正确的密钥

def sign(data):
    data['id'] = shop_id
    data = {k: v for k, v in data.items() if v}
    data = OrderedDict(sorted(data.items()))
    query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
    query = urllib.parse.unquote(query)
    data['sign'] = hashlib.md5((query + '&token=' + shop_token).encode()).hexdigest().upper()
    return data

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('🧪 使用正确密钥测试 OKPay API')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'App ID: {shop_id}')
print(f'密钥: {shop_token}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

# 测试创建支付链接
data = {
    'unique_id': 'TEST_CORRECT_TOKEN',
    'amount': '1',
    'coin': 'USDT',
    'name': '测试订单',
    'return_url': 'https://t.me/TGaccbbbot'
}

data = sign(data)
print(f'📤 请求数据: {data}\n')

response = requests.post('https://api.okaypay.me/shop/payLink', data=data)
result = response.json()

print(f'📥 响应结果: {result}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

if result.get('status') == 'success':
    print('✅ 成功！API 调用正常！')
    print(f'订单号: {result["data"]["order_id"]}')
    print(f'支付链接: {result["data"]["pay_url"]}')
else:
    print(f'❌ 失败: {result.get("msg")}')
