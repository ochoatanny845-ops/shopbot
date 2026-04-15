import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests, hashlib, urllib.parse
from collections import OrderedDict
import time

shop_id = "31443"
shop_token = "96feDimoURly5ABsEzGH1O3cYLt4w7an"

print('=' * 70)
print('🧪 测试 OKPay 回调机制')
print('=' * 70)

# 创建一个新的测试订单
unique_id = f'CALLBACK_TEST_{int(time.time())}'
print(f'\n📋 步骤 1: 创建支付链接')
print(f'测试订单号: {unique_id}')

data1 = {
    'amount': '0.1',  # 小额测试
    'coin': 'USDT',
    'return_url': 'https://t.me/TGaccbbbot',
    'name': '回调测试',
    'unique_id': unique_id,
    'callback_url': 'http://188.137.245.150:8888/okpay/callback',  # 单独订单回调
    'id': shop_id
}
data1 = OrderedDict(sorted(data1.items()))
query1 = urllib.parse.unquote(urllib.parse.urlencode(data1, quote_via=urllib.parse.quote))
sign_str1 = query1 + '&token=' + shop_token
data1['sign'] = hashlib.md5(sign_str1.encode()).hexdigest().upper()

response1 = requests.post('https://api.okaypay.me/shop/payLink', data=data1, timeout=10)
result1 = response1.json()

if result1.get('status') == 'success':
    order_id = result1['data']['order_id']
    pay_url = result1['data']['pay_url']
    
    print(f'\n✅ 支付链接创建成功')
    print(f'OKPay 订单号: {order_id}')
    print(f'商户订单号: {unique_id}')
    print(f'支付链接: {pay_url}')
    
    print('\n' + '=' * 70)
    print('📱 请立即点击支付链接并完成支付（0.1 USDT）')
    print('=' * 70)
    print(f'\n{pay_url}\n')
    print('=' * 70)
    print('支付后，查看回调服务器日志')
    print('如果 30 秒内没有收到回调，说明 OKPay 不会主动发送回调')
    print('=' * 70)
    
    # 等待回调
    print('\n⏳ 等待回调（30秒）...')
    print('（同时观察回调服务器日志）\n')
    
    for i in range(30):
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f'  {i + 1}秒...')
    
    print('\n' + '=' * 70)
    print('📋 查询订单状态')
    print('=' * 70)
    
    # 查询订单状态
    data2 = {
        'unique_id': unique_id,
        'id': shop_id
    }
    data2 = OrderedDict(sorted(data2.items()))
    query2 = urllib.parse.unquote(urllib.parse.urlencode(data2, quote_via=urllib.parse.quote))
    sign_str2 = query2 + '&token=' + shop_token
    data2['sign'] = hashlib.md5(sign_str2.encode()).hexdigest().upper()
    
    response2 = requests.post('https://api.okaypay.me/shop/checkDeposit', data=data2, timeout=10)
    result2 = response2.json()
    
    print(f'\n查询结果: {result2}')
    
    if result2.get('status') == 'success':
        status = result2['data']['status']
        print(f'\n订单状态: {status} (0=未付款, 1=已付款)')
        
        if status == 1:
            print('\n💡 结论:')
            print('✅ 用户已支付')
            print('❌ 但没有收到回调')
            print('📋 说明: OKPay 不会主动发送回调，需要商户主动轮询查询！')
        else:
            print('\n用户还未支付，无法判断回调是否工作')
    else:
        print(f'查询失败: {result2.get("msg")}')

else:
    print(f'\n❌ 创建支付链接失败: {result1.get("msg")}')

print('\n' + '=' * 70)
