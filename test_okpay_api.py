"""
测试 OKPay API 签名
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
import urllib.parse
from collections import OrderedDict
import requests

# 从你的截图中获取的配置
shop_id = "31439"
shop_token = "VdeDkTmGogXqRuylxvCGHKMbcFoLr4wZ"

# 测试数据
data = {
    'unique_id': 'TEST_001',
    'name': '测试订单',
    'amount': 1.0,
    'return_url': 'https://t.me/TGaccbbbot',
    'coin': 'USDT'
}

# 签名
data['id'] = shop_id

# 去除空值
data = {k: v for k, v in data.items() if v}

# 排序
data = OrderedDict(sorted(data.items()))

# 生成查询字符串
query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
query = urllib.parse.unquote(query)

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('📋 签名测试')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'shop_id: {shop_id}')
print(f'shop_token: {shop_token}')
print(f'数据: {data}')
print(f'查询字符串: {query}')
print(f'签名字符串: {query}&token={shop_token}')

# 签名
sign = hashlib.md5((query + '&token=' + shop_token).encode()).hexdigest().upper()
data['sign'] = sign

print(f'签名: {sign}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

# 请求
url = 'https://api.okaypay.me/shop/payLink'
print(f'🚀 发送请求: {url}')
print(f'📤 请求数据: {data}\n')

response = requests.post(url, data=data)
result = response.json()

print(f'📥 响应结果:')
print(f'状态码: {response.status_code}')
print(f'内容: {result}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

if result.get('status') == 'success':
    print('✅ API 调用成功！')
    print(f'支付链接: {result["data"]["pay_url"]}')
else:
    print(f'❌ API 调用失败: {result.get("msg")}')
