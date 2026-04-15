"""
使用新商户配置测试
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
import urllib.parse
from collections import OrderedDict
import requests

# ✅ 新的商户配置
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
print('🧪 测试新商户（启用后运行）')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'App ID: {shop_id}')
print(f'密钥: {shop_token}')
print(f'商户名称: TG111')
print('⚠️ 请先在 OKPay Bot 中启用商户！')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

# 测试创建支付链接
data = sign({
    'unique_id': 'TEST_ENABLED',
    'amount': '1',
    'coin': 'USDT',
    'name': 'TG111测试',
    'return_url': 'https://t.me/TGaccbbbot'
})

print(f'📤 请求: {data}\n')
response = requests.post('https://api.okaypay.me/shop/payLink', data=data)
result = response.json()

print(f'📥 响应: {result}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

if result.get('status') == 'success':
    print('\n✅✅✅ 成功！商户已启用，API 正常！✅✅✅')
    print(f'订单号: {result["data"]["order_id"]}')
    print(f'支付链接: {result["data"]["pay_url"]}')
    print('\n下一步:')
    print('1. 更新服务器 .env 文件中的密钥')
    print('2. 重启回调服务器')
    print('3. 重启销售机器人')
elif result.get('msg') == '未授权':
    print('\n❌ 还是"未授权"！')
    print('说明商户仍然是"已关闭"状态！')
    print('请在 OKPay Bot 中找到"启用商户"按钮！')
else:
    print(f'\n❌ 其他错误: {result.get("msg")}')
