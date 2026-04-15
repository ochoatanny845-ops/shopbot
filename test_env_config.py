import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os
from dotenv import load_dotenv

# 显示当前工作目录
print('=' * 60)
print(f'当前工作目录: {os.getcwd()}')

# 加载 .env 文件
env_path = os.path.join(os.getcwd(), '.env')
print(f'.env 文件路径: {env_path}')
print(f'.env 文件存在: {os.path.exists(env_path)}')

load_dotenv()

# 读取 OKPay 配置
OKPAY_SHOP_ID = os.getenv('OKPAY_SHOP_ID', '')
OKPAY_SHOP_TOKEN = os.getenv('OKPAY_SHOP_TOKEN', '')
OKPAY_CALLBACK_PORT = os.getenv('OKPAY_CALLBACK_PORT', '8888')
OKPAY_BOT_USERNAME = os.getenv('OKPAY_BOT_USERNAME', 'TGaccbbbot')

print('=' * 60)
print('读取到的配置:')
print(f'OKPAY_SHOP_ID: {OKPAY_SHOP_ID}')
print(f'OKPAY_SHOP_TOKEN: {OKPAY_SHOP_TOKEN}')
print(f'OKPAY_CALLBACK_PORT: {OKPAY_CALLBACK_PORT}')
print(f'OKPAY_BOT_USERNAME: {OKPAY_BOT_USERNAME}')
print('=' * 60)

if not OKPAY_SHOP_ID or not OKPAY_SHOP_TOKEN:
    print('\n❌ OKPay 配置为空！')
    print('\n检查:')
    print('1. .env 文件是否在当前目录')
    print('2. .env 文件格式是否正确（不要有多余空格）')
    print('3. 环境变量名称是否正确')
else:
    print('\n✅ OKPay 配置读取成功！')
    
    # 测试 API
    print('\n测试 OKPay API...')
    import requests, hashlib, urllib.parse
    from collections import OrderedDict
    
    data = {'id': OKPAY_SHOP_ID}
    data = OrderedDict(sorted(data.items()))
    query = urllib.parse.unquote(urllib.parse.urlencode(data, quote_via=urllib.parse.quote))
    sign_str = query + '&token=' + OKPAY_SHOP_TOKEN
    data['sign'] = hashlib.md5(sign_str.encode()).hexdigest().upper()
    
    print(f'请求数据: {dict(data)}')
    
    response = requests.post('https://api.okaypay.me/shop/balance', data=data, timeout=10)
    result = response.json()
    
    print(f'响应: {result}')
    
    if result.get('status') == 'success':
        print('\n✅ API 调用成功！')
    else:
        print(f'\n❌ API 调用失败: {result.get("msg")}')
