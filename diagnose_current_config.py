import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\shopbot')

print('=' * 70)
print('诊断 OKPay 配置和 API')
print('=' * 70)

# 1. 检查配置
print('\n📋 步骤 1: 检查配置文件')
from config import Config
print(f'OKPAY_SHOP_ID: {Config.OKPAY_SHOP_ID}')
print(f'OKPAY_SHOP_TOKEN: {Config.OKPAY_SHOP_TOKEN}')
print(f'OKPAY_BOT_USERNAME: {Config.OKPAY_BOT_USERNAME}')

if not Config.OKPAY_SHOP_ID or not Config.OKPAY_SHOP_TOKEN:
    print('❌ 配置未读取！检查 .env 文件！')
    sys.exit(1)

print('✅ 配置读取成功')

# 2. 测试 OKPayHandler
print('\n📋 步骤 2: 测试 OKPayHandler')
from okpay_handler import OKPayHandler

handler = OKPayHandler()
print(f'Handler shop_id: {handler.shop_id}')
print(f'Handler shop_token: {handler.shop_token}')

# 3. 创建支付链接
print('\n📋 步骤 3: 创建支付链接')
import time
unique_id = f'TEST_{int(time.time())}'
result = handler.create_payment_link(unique_id, 1.0, 'USDT')

print(f'\n结果: {result}')

if result['success']:
    print('\n✅ 成功！')
    print(f'订单号: {result["order_id"]}')
    print(f'支付链接: {result["pay_url"]}')
else:
    print(f'\n❌ 失败: {result["message"]}')

print('\n' + '=' * 70)
