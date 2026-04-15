"""
使用 OKPay 官方代码测试
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
from math import log
import urllib.parse
from collections import OrderedDict
import requests
from urllib.parse import urlencode, quote

api_url = 'https://api.okaypay.me/shop/'
shop_id = "31439"
shop_token = "VdeDkTmGogXqRuylxvCGHKMbcFoLr4wZ"
NAME = "测试商城"
bot_username = "TGaccbbbot"

# 数据签名（OKPay 官方代码）
def sign(data):
    data['id'] = shop_id
    data = {k: v for k, v in data.items() if v}  # 去除空值
    data = OrderedDict(sorted(data.items()))  # 按照key排序
    query = urllib.parse.urlencode(data,quote_via=urllib.parse.quote) # 请求参数拼接
    query = urllib.parse.unquote(query)  # 请求参数解码
    data['sign'] = hashlib.md5((query + '&token=' + shop_token).encode()).hexdigest().upper()
    return data

#OKpay 存款API（OKPay 官方代码）
def okpay_deposit_api(order_number, amount, coin='USDT', bot_id=None):
    data = {
        'unique_id': order_number,
        'name': f'{NAME}存款',
        'amount': amount,
        'return_url': f'https://t.me/{bot_username}',
        'coin': coin
    }
    data = sign(data)

    deposit_api_url = api_url + 'payLink'
    response = requests.post(deposit_api_url, data=data)
    return response.json()

# 测试
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('🧪 使用 OKPay 官方代码测试')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'shop_id: {shop_id}')
print(f'shop_token: {shop_token}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

result = okpay_deposit_api('TEST_OFFICIAL_001', 1.0)

print(f'📥 响应结果: {result}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

if result.get('status') == 'success':
    print('✅ 官方代码调用成功！')
    print(f'支付链接: {result["data"]["pay_url"]}')
else:
    print(f'❌ 官方代码也失败: {result.get("msg")}')
    print('\n⚠️ 说明问题不在签名逻辑，而是：')
    print('   1. shop_id 或 shop_token 不正确')
    print('   2. 商户账号状态异常')
    print('   3. OKPay 平台问题')
