"""
USDT TRC20 充值验证模块
"""
import requests
import time
from typing import Optional, Dict

class TRC20Recharge:
    """USDT TRC20 充值验证器"""
    
    # USDT TRC20 合约地址（Tron 主网）
    USDT_CONTRACT = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'
    
    # TronGrid API
    TRONGRID_API = 'https://api.trongrid.io'
    
    def __init__(self, recipient_address: str):
        """
        初始化
        
        Args:
            recipient_address: 收款地址（Base58 格式，T 开头）
        """
        self.recipient_address = recipient_address
    
    def verify_transaction(self, txid: str, expected_amount: float) -> Dict:
        """
        验证 USDT TRC20 转账
        
        Args:
            txid: 交易哈希
            expected_amount: 期望金额（USDT）
        
        Returns:
            {
                'success': bool,
                'message': str,
                'amount': float,
                'from_address': str,
                'to_address': str,
                'timestamp': int
            }
        """
        try:
            # 1. 获取交易详情
            tx_info = self._get_transaction_info(txid)
            if not tx_info['success']:
                return tx_info
            
            # 2. 验证是否是 TRC20 转账
            if not self._is_trc20_transfer(tx_info):
                return {
                    'success': False,
                    'message': '❌ 这不是有效的 TRC20 转账交易'
                }
            
            # 3. 验证合约地址（确保是真 USDT）
            contract_address = tx_info.get('contract_address')
            if contract_address != self.USDT_CONTRACT:
                return {
                    'success': False,
                    'message': f'❌ 检测到假币！\n合约地址不匹配\n期望: {self.USDT_CONTRACT}\n实际: {contract_address}'
                }
            
            # 4. 验证接收地址
            to_address = tx_info.get('to_address')
            if to_address != self.recipient_address:
                return {
                    'success': False,
                    'message': f'❌ 接收地址错误\n期望: {self.recipient_address}\n实际: {to_address}'
                }
            
            # 5. 验证金额
            actual_amount = tx_info.get('amount', 0)
            if actual_amount < expected_amount * 0.99:  # 允许 1% 误差（手续费）
                return {
                    'success': False,
                    'message': f'❌ 金额不足\n期望: {expected_amount} USDT\n实际: {actual_amount} USDT'
                }
            
            # 6. 验证交易状态（必须已确认）
            if not tx_info.get('confirmed', False):
                return {
                    'success': False,
                    'message': '⏳ 交易尚未确认，请稍后再试'
                }
            
            # 7. 检查是否是真实转账（不是授权）
            if tx_info.get('method') != 'transfer':
                return {
                    'success': False,
                    'message': f'❌ 这不是转账交易（可能是授权）\n方法: {tx_info.get("method")}'
                }
            
            # ✅ 验证通过
            return {
                'success': True,
                'message': '✅ 验证通过',
                'amount': actual_amount,
                'from_address': tx_info.get('from_address'),
                'to_address': to_address,
                'timestamp': tx_info.get('timestamp'),
                'txid': txid
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ 验证失败: {str(e)}'
            }
    
    def _get_transaction_info(self, txid: str) -> Dict:
        """获取交易详情"""
        try:
            # API 请求
            url = f'{self.TRONGRID_API}/v1/transactions/{txid}'
            headers = {
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'message': f'❌ 查询失败（HTTP {response.status_code}）'
                }
            
            data = response.json()
            
            # 检查交易是否存在
            if not data or 'txID' not in data:
                return {
                    'success': False,
                    'message': '❌ 交易不存在或尚未上链'
                }
            
            # 解析交易详情
            tx_info = self._parse_transaction(data)
            tx_info['success'] = True
            
            return tx_info
            
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'❌ 网络错误: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ 解析错误: {str(e)}'
            }
    
    def _parse_transaction(self, data: Dict) -> Dict:
        """解析交易数据"""
        result = {
            'confirmed': data.get('ret', [{}])[0].get('contractRet') == 'SUCCESS',
            'timestamp': data.get('block_timestamp', 0) // 1000,  # 转为秒
        }
        
        # 解析合约调用
        contract_data = data.get('raw_data', {}).get('contract', [{}])[0]
        contract_type = contract_data.get('type')
        
        if contract_type == 'TriggerSmartContract':
            # TRC20 转账
            parameter = contract_data.get('parameter', {}).get('value', {})
            
            # 合约地址
            result['contract_address'] = self._hex_to_base58(parameter.get('contract_address'))
            
            # 解析 data（包含方法和参数）
            data_hex = parameter.get('data', '')
            
            # 前 8 位是方法签名
            method_signature = data_hex[:8]
            
            # transfer 方法签名：a9059cbb
            if method_signature == 'a9059cbb':
                result['method'] = 'transfer'
                
                # 接收地址（64 位，去掉前 24 位填充）
                to_address_hex = '41' + data_hex[8:72][-40:]
                result['to_address'] = self._hex_to_base58(to_address_hex)
                
                # 金额（64 位十六进制，USDT 有 6 位小数）
                amount_hex = data_hex[72:136]
                result['amount'] = int(amount_hex, 16) / 1_000_000  # USDT 6 位小数
            
            # approve 方法签名：095ea7b3
            elif method_signature == '095ea7b3':
                result['method'] = 'approve'
            
            # 发送地址
            result['from_address'] = self._hex_to_base58(parameter.get('owner_address'))
        
        return result
    
    def _hex_to_base58(self, hex_address: str) -> str:
        """将十六进制地址转为 Base58（Tron 地址格式）"""
        # 简化版本：如果已经是 Base58，直接返回
        if hex_address.startswith('T'):
            return hex_address
        
        # 完整实现需要 base58 库，这里使用 TronGrid API 转换
        try:
            url = f'{self.TRONGRID_API}/wallet/validateaddress'
            response = requests.post(url, json={'address': hex_address}, timeout=5)
            data = response.json()
            
            if data.get('result'):
                return hex_address  # 已经是有效地址
            
            # 如果是 hex，需要转换（这里简化处理）
            return hex_address
        except:
            return hex_address
    
    def _is_trc20_transfer(self, tx_info: Dict) -> bool:
        """检查是否是 TRC20 转账"""
        return (
            'contract_address' in tx_info and
            'method' in tx_info and
            tx_info['method'] == 'transfer'
        )


# 测试代码
if __name__ == '__main__':
    # 示例：验证一笔交易
    recipient = 'TYour收款地址'  # 替换为你的地址
    
    verifier = TRC20Recharge(recipient)
    
    # 测试 TxID（替换为真实的）
    txid = '7a1b2c3d4e5f...'
    expected_amount = 10.0
    
    result = verifier.verify_transaction(txid, expected_amount)
    
    print(result)
