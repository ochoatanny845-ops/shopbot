"""
测试 TRC20 充值验证
验证收款地址是否有效
"""
from trc20_recharge import TRC20Recharge
from config import Config

# 从配置文件读取
RECIPIENT_ADDRESS = Config.USDT_RECEIVER_ADDRESS
API_KEY = Config.TRONGRID_API_KEY if hasattr(Config, 'TRONGRID_API_KEY') else None

print('='*60)
print('🔍 测试 USDT TRC20 充值验证功能')
print('='*60)

print(f'\n收款地址: {RECIPIENT_ADDRESS}')
print(f'地址长度: {len(RECIPIENT_ADDRESS)} 字符')
print(f'地址格式: {"✅ 正确 (T 开头)" if RECIPIENT_ADDRESS.startswith("T") else "❌ 错误"}')
print(f'API Key: {"✅ 已配置" if API_KEY else "⚠️ 未配置（使用免费版）"}')

# 创建验证器
verifier = TRC20Recharge(RECIPIENT_ADDRESS, API_KEY)
print('\n✅ 验证器初始化成功')

print('\n' + '='*60)
print('📋 测试说明：')
print('='*60)
print('''
要测试充值功能，请：

1. 向以下地址转账少量 USDT（例如 1 USDT）
   地址：TV77o3KfH8DkQNNEsvDLNo765ABcqr3MnM
   网络：TRC20 (Tron)

2. 转账完成后，复制交易哈希（TxID）

3. 运行测试：
   python test_recharge_verify.py <TxID> <金额>
   
   例如：
   python test_recharge_verify.py 7a1b2c3d4e5f... 1.0

4. 系统将验证：
   ✅ 真实 USDT（非假币）
   ✅ 真实转账（非授权）
   ✅ 接收地址正确
   ✅ 金额匹配
   ✅ 交易已确认
''')

print('='*60)
print('⏸ 等待你完成测试转账...')
print('='*60)

# 如果提供了命令行参数，进行验证
import sys
if len(sys.argv) >= 3:
    txid = sys.argv[1]
    expected_amount = float(sys.argv[2])
    
    print(f'\n🔍 开始验证...')
    print(f'TxID: {txid}')
    print(f'期望金额: {expected_amount} USDT')
    print('-'*60)
    
    result = verifier.verify_transaction(txid, expected_amount)
    
    if result['success']:
        print('✅ 验证成功！')
        print(f"\n详细信息：")
        print(f"  实际金额: {result['amount']} USDT")
        print(f"  发送地址: {result['from_address']}")
        print(f"  接收地址: {result['to_address']}")
        print(f"  交易时间: {result['timestamp']}")
        print(f"  交易哈希: {result['txid']}")
    else:
        print('❌ 验证失败！')
        print(f"\n错误信息：")
        print(f"  {result['message']}")
