import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests, hashlib, urllib.parse
from collections import OrderedDict

# 你的商户配置
shop_id = "31439"
shop_token = "9VdfeDiGoUXRuv5ACE1MbFhL0tr47Za"

print('=' * 60)
print('测试 OKPay balance 接口')
print('=' * 60)

# 按文档示例格式签名
data = {'id': shop_id}
data = OrderedDict(sorted(data.items()))

# 生成查询字符串（完全按文档格式）
query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
query = urllib.parse.unquote(query)

# 签名字符串
sign_string = query + '&token=' + shop_token

# 计算签名
sign = hashlib.md5(sign_string.encode()).hexdigest().upper()

data['sign'] = sign

print(f'商户ID: {shop_id}')
print(f'密钥: {shop_token}')
print(f'查询字符串: {query}')
print(f'签名字符串: {sign_string}')
print(f'签名: {sign}')
print(f'请求数据: {dict(data)}')
print('=' * 60)

# 发送请求
url = 'https://api.okaypay.me/shop/balance'
print(f'\n请求 URL: {url}')
print('发送请求...\n')

response = requests.post(url, data=data, timeout=10)

print(f'HTTP 状态码: {response.status_code}')
print(f'响应内容: {response.text}')
print('=' * 60)

result = response.json()

if result.get('status') == 'success':
    print('\n✅ 成功！')
    print(f'USDT 余额: {result["data"].get("usdt")}')
    print(f'TRX 余额: {result["data"].get("trx")}')
    print(f'CNY 余额: {result["data"].get("cny")}')
else:
    print(f'\n❌ 失败: {result.get("msg")}')
    
    # 如果还是未授权，给出详细建议
    if result.get('msg') == '未授权':
        print('\n已确认配置正确但仍"未授权"，可能原因:')
        print('1. 商户账号需要在 OKPay Bot 中做额外激活操作')
        print('2. 商户 API 功能未开通（需要申请或开通）')
        print('3. OKPay 平台问题或限制')
        print('4. 商户账号类型不支持 API（可能需要升级）')
        print('\n建议: 在 OKPay Bot 中找客服或查看是否有"API 开通"选项')
