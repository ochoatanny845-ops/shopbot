"""
余额监控服务
独立运行，定期检查源机器人和 OKPay 余额，低于阈值时通知管理员
"""
import asyncio
import os
from datetime import datetime
from telethon import TelegramClient
from config import Config
from database import Database

class BalanceMonitor:
    """余额监控器"""
    
    # 余额预警阈值
    SOURCE_BOT_THRESHOLD = 20.0  # 源机器人余额阈值（USDT）
    OKPAY_THRESHOLD = 20.0       # OKPay 钱包余额阈值（USDT）
    
    # 检查间隔（秒）
    CHECK_INTERVAL = 3600  # 每小时检查一次
    
    def __init__(self):
        self.db = Database()
        self.client = None
        self.last_warning_time = {}  # 记录上次预警时间（避免频繁通知）
    
    async def start(self):
        """启动监控服务"""
        print('🔍 余额监控服务启动中...')
        
        from client_manager import ClientManager
        self.client = await ClientManager.get_client()
        
        print('✅ 余额监控服务已启动')
        print(f'⏱ 检查间隔: {self.CHECK_INTERVAL}秒 ({self.CHECK_INTERVAL // 60}分钟)')
        print(f'⚠️ 源机器人阈值: ${self.SOURCE_BOT_THRESHOLD}')
        print(f'⚠️ OKPay 阈值: ${self.OKPAY_THRESHOLD}')
        print('='*50)
        
        # 启动定期检查
        while True:
            try:
                await self.check_all_balances()
            except Exception as e:
                print(f'❌ 检查余额时出错: {e}')
            
            # 等待下次检查
            await asyncio.sleep(self.CHECK_INTERVAL)
    
    async def check_all_balances(self):
        """检查所有余额"""
        print(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 开始检查余额...')
        
        # 1. 检查源机器人余额
        source_balance = await self.check_source_bot_balance()
        if source_balance is not None:
            if source_balance < self.SOURCE_BOT_THRESHOLD:
                await self.send_warning(
                    'source_bot',
                    f'⚠️ **源机器人余额预警**\n\n'
                    f'🏦 当前余额: ${source_balance:.2f}\n'
                    f'⚠️ 预警阈值: ${self.SOURCE_BOT_THRESHOLD}\n'
                    f'💰 建议充值: ${self.SOURCE_BOT_THRESHOLD - source_balance + 10:.2f}\n\n'
                    f'请及时充值以确保订单正常处理'
                )
            else:
                print(f'  ✅ 源机器人余额充足: ${source_balance:.2f}')
        
        # 2. 检查 OKPay 钱包余额
        okpay_balance = await self.check_okpay_balance()
        if okpay_balance is not None:
            if okpay_balance < self.OKPAY_THRESHOLD:
                await self.send_warning(
                    'okpay',
                    f'⚠️ **OKPay 钱包余额预警**\n\n'
                    f'💳 当前余额: ${okpay_balance:.2f}\n'
                    f'⚠️ 预警阈值: ${self.OKPAY_THRESHOLD}\n'
                    f'💰 建议充值: ${self.OKPAY_THRESHOLD - okpay_balance + 10:.2f}\n\n'
                    f'请及时充值 OKPay 钱包'
                )
            else:
                print(f'  ✅ OKPay 余额充足: ${okpay_balance:.2f}')
        
        print('检查完成')
        print('='*50)
    
    async def check_source_bot_balance(self):
        """查询源机器人余额"""
        try:
            # 发送主菜单命令
            await self.client.send_message(Config.SOURCE_BOT, '🏠主菜单')
            await asyncio.sleep(2)
            
            # 获取最新消息
            msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
            
            if msgs and msgs[0]:
                text = msgs[0].message if hasattr(msgs[0], 'message') else msgs[0].text
                
                if not text:
                    return None
                
                # 解析余额
                import re
                patterns = [
                    r'USDT\s*[:：]\s*(\d+\.?\d*)',
                    r'余额\s*[:：]\s*(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*USDT',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        balance = float(match.group(1))
                        return balance
            
            return None
        except Exception as e:
            print(f'  ❌ 查询源机器人余额失败: {e}')
            return None
    
    async def check_okpay_balance(self):
        """查询 OKPay 钱包余额"""
        try:
            # 发送余额查询命令
            await self.client.send_message('@okpay', '/balance')
            await asyncio.sleep(2)
            
            # 获取最新消息
            msgs = await self.client.get_messages('@okpay', limit=1)
            
            if msgs and msgs[0]:
                text = msgs[0].message if hasattr(msgs[0], 'message') else msgs[0].text
                
                if not text:
                    return None
                
                # 解析余额（例如：Balance: 15.23 USDT）
                import re
                patterns = [
                    r'Balance\s*[:：]\s*(\d+\.?\d*)',
                    r'余额\s*[:：]\s*(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*USDT',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        balance = float(match.group(1))
                        return balance
            
            return None
        except Exception as e:
            print(f'  ❌ 查询 OKPay 余额失败: {e}')
            return None
    
    async def send_warning(self, warning_type, message):
        """发送预警通知（避免频繁通知）"""
        now = datetime.now()
        
        # 检查上次预警时间（同类型预警间隔至少 6 小时）
        if warning_type in self.last_warning_time:
            last_time = self.last_warning_time[warning_type]
            elapsed = (now - last_time).total_seconds()
            
            if elapsed < 21600:  # 6 小时 = 21600 秒
                print(f'  ⏭ 跳过预警（距上次预警 {elapsed // 60:.0f} 分钟）')
                return
        
        # 发送预警
        try:
            for admin_id in Config.ADMIN_IDS:
                await self.client.send_message(admin_id, message)
                print(f'  ✅ 已通知管理员 {admin_id}')
            
            # 记录预警时间
            self.last_warning_time[warning_type] = now
        except Exception as e:
            print(f'  ❌ 发送预警失败: {e}')
    
    async def stop(self):
        """停止监控服务"""
        if self.client:
            await self.client.disconnect()
        print('👋 余额监控服务已停止')

async def main():
    """主函数"""
    monitor = BalanceMonitor()
    try:
        await monitor.start()
    except KeyboardInterrupt:
        print('\n收到停止信号')
    finally:
        await monitor.stop()

if __name__ == '__main__':
    asyncio.run(main())
