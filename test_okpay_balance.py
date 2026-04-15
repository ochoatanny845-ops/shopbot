"""
测试 OKPay 查询余额接口
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

# 签名
def sign(data):
    data['id'] = shop_id
    data = {k: v for k, v in data.items() if v}
    data = OrderedDict(sorted(data.items()))
    query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
    query = urllib.parse.unquote(query)
    data['sign'] = hashlib.md5((query + '&token=' + shop_token).encode()).hexdigest().upper()
    return data

# 测试查询余额
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('🧪 测试 OKPay 查询余额接口')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

data = {}
data = sign(data)

url = 'https://api.okaypay.me/shop/balance'
print(f'🚀 请求: {url}')
print(f'📤 参数: {data}\n')

response = requests.post(url, data=data)
result = response.json()

print(f'📥 响应: {result}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

if result.get('status') == 'success':
    print('✅ 查询余额成功！')
    print(f'余额信息: {result.get("data")}')
else:
    print(f'❌ 查询失败: {result.get("msg")}')
    
    if result.get('msg') == '未授权':
        print('\n⚠️ 说明：')
        print('   1. API 功能未开通')
        print('   2. 需要联系客服开通权限')
        print('   3. 可能需要商户认证')
