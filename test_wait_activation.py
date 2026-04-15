"""
持续测试 - 等待商户激活生效
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
import urllib.parse
from collections import OrderedDict
import requests
import time

shop_id = "31439"
shop_token = "9VdfeDiGoUXRuv5ACE1MbFhL0tr47Za"

def sign(data):
    data['id'] = shop_id
    data = {k: v for k, v in data.items() if v is not None and v != ''}
    data = OrderedDict(sorted(data.items()))
    query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
    query = urllib.parse.unquote(query)
    data['sign'] = hashlib.md5((query + '&token=' + shop_token).encode()).hexdigest().upper()
    return data

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('🔄 持续测试 - 每30秒一次')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'App ID: {shop_id}')
print(f'密钥: {shop_token}')
print(f'测试次数: 5次（每30秒一次）')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

for i in range(5):
    print(f'⏰ 第 {i+1} 次测试 ({time.strftime("%H:%M:%S")})')
    
    data = sign({
        'amount': '1',
        'coin': 'USDT'
    })
    
    response = requests.post('https://api.okaypay.me/shop/payLink', data=data)
    result = response.json()
    
    if result.get('status') == 'success':
        print(f'✅ 成功！')
        print(f'订单号: {result["data"]["order_id"]}')
        print(f'支付链接: {result["data"]["pay_url"]}')
        print('\n🎉 商户已激活，API 可用！')
        break
    elif result.get('msg') == '未授权':
        print(f'❌ 仍然"未授权"')
    else:
        print(f'⚠️ 其他错误: {result.get("msg")}')
    
    if i < 4:
        print(f'等待30秒...\n')
        time.sleep(30)

print('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('测试完成')
