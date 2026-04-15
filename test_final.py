"""
使用截图中的完整配置测试
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import hashlib
import urllib.parse
from collections import OrderedDict
import requests

# 从最新截图中提取的配置
shop_id = "31439"
shop_token = "VdeDkTmGogXgRuvkyCGHKMbcFpLr4wZ"

def sign(data):
    data['id'] = shop_id
    # 去除空值
    data = {k: v for k, v in data.items() if v is not None and v != ''}
    # 排序
    data = OrderedDict(sorted(data.items()))
    # 生成查询字符串
    query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
    query = urllib.parse.unquote(query)
    # 签名
    data['sign'] = hashlib.md5((query + '&token=' + shop_token).encode()).hexdigest().upper()
    return data

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('🔍 最终测试 - 完整配置')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'App ID: {shop_id}')
print(f'密钥: {shop_token}')
print(f'商户名称: TGACC')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

# 测试 1：查询余额
print('📋 测试 1: 查询商户余额')
data1 = sign({})
print(f'请求: {data1}')
response1 = requests.post('https://api.okaypay.me/shop/balance', data=data1)
result1 = response1.json()
print(f'响应: {result1}\n')

# 测试 2：创建支付链接（最简参数）
print('📋 测试 2: 创建支付链接（最简参数）')
data2 = sign({
    'amount': '1',
    'coin': 'USDT'
})
print(f'请求: {data2}')
response2 = requests.post('https://api.okaypay.me/shop/payLink', data=data2)
result2 = response2.json()
print(f'响应: {result2}\n')

# 测试 3：创建支付链接（完整参数）
print('📋 测试 3: 创建支付链接（完整参数）')
data3 = sign({
    'unique_id': 'FINAL_TEST_001',
    'name': 'TGACC充值',
    'amount': '1',
    'return_url': 'https://t.me/TGaccbbbot',
    'coin': 'USDT'
})
print(f'请求: {data3}')
response3 = requests.post('https://api.okaypay.me/shop/payLink', data=data3)
result3 = response3.json()
print(f'响应: {result3}\n')

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

# 汇总结果
if result1.get('status') == 'success' or result2.get('status') == 'success' or result3.get('status') == 'success':
    print('✅ 至少一个接口成功！')
    if result1.get('status') == 'success':
        print(f'商户余额: {result1["data"]}')
    if result2.get('status') == 'success' or result3.get('status') == 'success':
        print('支付链接创建成功！')
else:
    print('❌ 所有接口都失败！')
    print('\n可能的原因:')
    print('1. 商户账号确实有问题（需要人工激活）')
    print('2. OKPay 平台限制（地区、IP、时间）')
    print('3. 这个商户 ID 不是最新的（可能有多个商户）')
    print('\n建议:')
    print('1. 在 OKPay Bot 中确认只有一个商户账号')
    print('2. 尝试删除并重新创建商户')
    print('3. 或暂时放弃 OKPay，使用 TRC20 充值')
