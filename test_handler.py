import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\shopbot')

from okpay_handler import OKPayHandler

print('=' * 60)
print('测试 OKPayHandler 类')
print('=' * 60)

# 创建处理器实例
handler = OKPayHandler()

print(f'商户 ID: {handler.shop_id}')
print(f'密钥: {handler.shop_token}')
print('=' * 60)

# 测试创建支付链接
print('\n📋 测试 1: 创建支付链接')
result = handler.create_payment_link('TEST_HANDLER_001', 1.0, 'USDT')
print(f'结果: {result}')

print('\n=' * 60)
