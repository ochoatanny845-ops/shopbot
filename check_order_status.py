import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests, hashlib, urllib.parse
from collections import OrderedDict

shop_id = "31443"
shop_token = "96feDimoURly5ABsEzGH1O3cYLt4w7an"

# 从截图中的订单号
unique_id = "8"  # 销售机器人的订单号

print('=' * 60)
print('查询 OKPay 订单状态')
print('=' * 60)
print(f'商户订单号: {unique_id}')
print('=' * 60)

# 查询订单状态
data = {
    'unique_id': unique_id,
    'id': shop_id
}
data = OrderedDict(sorted(data.items()))
query = urllib.parse.unquote(urllib.parse.urlencode(data, quote_via=urllib.parse.quote))
sign_str = query + '&token=' + shop_token
data['sign'] = hashlib.md5(sign_str.encode()).hexdigest().upper()

print(f'\n请求数据: {dict(data)}')

response = requests.post('https://api.okaypay.me/shop/checkDeposit', data=data, timeout=10)
result = response.json()

print(f'\n响应: {result}')
print('=' * 60)

if result.get('status') == 'success':
    print('\n✅ 查询成功！')
    print(f'OKPay 订单号: {result["data"]["order_id"]}')
    print(f'商户订单号: {result["data"]["unique_id"]}')
    print(f'状态: {result["data"]["status"]} (0=未付款, 1=已付款)')
    print(f'金额: {result["data"]["amount"]}')
    
    if result["data"]["status"] == 1:
        print('\n💰 用户已支付！需要手动给用户加余额！')
    else:
        print('\n⏳ 用户还未支付')
else:
    print(f'\n❌ 查询失败: {result.get("msg")}')
