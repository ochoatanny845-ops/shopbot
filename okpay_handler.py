"""
OKPay API 处理器
"""
import hashlib
import urllib.parse
from collections import OrderedDict
import requests
from config import Config

class OKPayHandler:
    """OKPay API 封装"""
    
    API_URL = 'https://api.okaypay.me/shop/'
    
    def __init__(self):
        self.shop_id = Config.OKPAY_SHOP_ID
        self.shop_token = Config.OKPAY_SHOP_TOKEN
        self.bot_username = Config.OKPAY_BOT_USERNAME
    
    def create_payment_link(self, unique_id: str, amount: float, coin: str = 'USDT') -> dict:
        """
        创建支付链接
        
        Args:
            unique_id: 唯一订单号
            amount: 金额
            coin: 货币类型（USDT/TRX）
        
        Returns:
            {
                'success': bool,
                'order_id': str,
                'pay_url': str,
                'message': str
            }
        """
        try:
            data = {
                'unique_id': str(unique_id),
                'name': '账号商城充值',
                'amount': str(amount),
                'return_url': f'https://t.me/{self.bot_username}',
                'coin': str(coin),
                'callback_url': f'http://188.137.245.150:{Config.OKPAY_CALLBACK_PORT}/okpay/callback'
            }
            
            # 签名
            data = self._sign(data)
            
            # 请求
            url = self.API_URL + 'payLink'
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            print(f'  📡 OKPay 创建支付链接: {result}')
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'order_id': result['data']['order_id'],
                    'pay_url': result['data']['pay_url'],
                    'message': '支付链接创建成功'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', '创建支付链接失败')
                }
        
        except Exception as e:
            print(f'  ❌ OKPay API 错误: {e}')
            return {
                'success': False,
                'message': f'API 错误: {str(e)}'
            }
    
    def check_deposit(self, unique_id: str) -> dict:
        """
        查询充值订单状态
        
        Args:
            unique_id: 唯一订单号
        
        Returns:
            {
                'success': bool,
                'status': int,  # 0未付款 1已付款
                'amount': float,
                'message': str
            }
        """
        try:
            data = {
                'unique_id': unique_id
            }
            
            # 签名
            data = self._sign(data)
            
            # 请求
            url = self.API_URL + 'checkDeposit'
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            print(f'  🔍 OKPay 查询订单: {result}')
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'status': result['data']['status'],
                    'amount': float(result['data']['amount']),
                    'order_id': result['data']['order_id'],
                    'message': '查询成功'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', '查询失败')
                }
        
        except Exception as e:
            print(f'  ❌ OKPay 查询错误: {e}')
            return {
                'success': False,
                'message': f'查询错误: {str(e)}'
            }
    
    def verify_callback(self, data: dict) -> bool:
        """
        验证回调签名
        
        Args:
            data: 回调数据
        
        Returns:
            bool: 签名是否有效
        """
        try:
            sign = data.pop('sign', None)
            
            if not sign:
                print('  ❌ 回调缺少签名')
                return False
            
            # 过滤空值
            filtered_data = {k: v for k, v in data.items() if v}
            
            # 排序
            sorted_data = OrderedDict(sorted(filtered_data.items()))
            
            # 生成查询字符串
            pairs = self._http_build_query(sorted_data)
            query_string = "&".join([f"{k}={v}" for k, v in pairs])
            
            # 计算签名
            expected_sign = hashlib.md5(
                (query_string + '&token=' + self.shop_token).encode()
            ).hexdigest().upper()
            
            print(f'  🔐 签名验证:')
            print(f'    查询字符串: {query_string}')
            print(f'    期望签名: {expected_sign}')
            print(f'    实际签名: {sign}')
            
            return expected_sign == sign
        
        except Exception as e:
            print(f'  ❌ 签名验证错误: {e}')
            return False
    
    def _sign(self, data: dict) -> dict:
        """数据签名"""
        data['id'] = self.shop_id
        
        # 去除空值
        data = {k: v for k, v in data.items() if v}
        
        # 排序
        data = OrderedDict(sorted(data.items()))
        
        # 生成查询字符串
        query = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)
        query = urllib.parse.unquote(query)
        
        # 签名
        data['sign'] = hashlib.md5(
            (query + '&token=' + self.shop_token).encode()
        ).hexdigest().upper()
        
        return data
    
    def _http_build_query(self, data: dict, prefix: str = '') -> list:
        """将 Python 字典转换为 PHP 风格的查询字符串"""
        result = []
        for key, value in data.items():
            if isinstance(value, dict):
                result.extend(
                    self._http_build_query(
                        value,
                        f"{prefix}{key}[" if not prefix else f"{prefix}{key}["
                    )
                )
            else:
                # 键：保留 [] 不编码
                encoded_key = urllib.parse.quote(
                    f"{prefix}{key}]" if '[' in prefix else f"{prefix}{key}",
                    safe='[]'
                )
                
                # 值：保留 + 和 - 不编码
                encoded_value = urllib.parse.quote(str(value), safe='+-')
                
                result.append((encoded_key, encoded_value))
        
        return result
