"""
多账号轮换刷新管理器
- 20个账号轮流抓取商品
- 每1分钟换一个账号
- 自动检测封禁并告警
- 可用账号<5个时发送警告
"""
import asyncio
import json
import time
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import AuthKeyUnregisteredError, UserDeactivatedBanError
from scraper import ProductScraper
from config import Config

class ScraperPoolManager:
    """刷新器账号池管理器"""
    
    def __init__(self, config_file='accounts_pool.json'):
        self.config_file = config_file
        self.accounts = []
        self.current_index = 0
        self.rotation_interval = 60  # 默认1分钟
        self.banned_notify_sent = set()
        self.low_accounts_notified = False
        self.load_config()
    
    def load_config(self):
        """加载账号配置"""
        if not os.path.exists(self.config_file):
            print(f'⚠️ 配置文件不存在: {self.config_file}')
            print(f'💡 请先运行 upload_accounts.py 上传账号')
            self.accounts = []
            return
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.accounts = data.get('accounts', [])
            self.current_index = data.get('current_index', 0)
            self.rotation_interval = data.get('rotation_interval', 60)
        
        print(f'✅ 加载了 {len(self.accounts)} 个账号')
        print(f'⏱️ 轮换间隔: {self.rotation_interval} 秒')
    
    def save_config(self):
        """保存账号状态"""
        data = {
            'accounts': self.accounts,
            'current_index': self.current_index,
            'rotation_interval': self.rotation_interval
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_next_account(self):
        """获取下一个可用账号（轮换）"""
        if not self.accounts:
            return None
        
        tried = 0
        while tried < len(self.accounts):
            account = self.accounts[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.accounts)
            
            if account['status'] == 'active':
                return account
            
            tried += 1
        
        return None  # 没有可用账号
    
    def count_active_accounts(self):
        """统计可用账号数量"""
        return sum(1 for acc in self.accounts if acc['status'] == 'active')
    
    async def check_if_banned(self, client, account):
        """检测账号是否被封"""
        try:
            # 尝试获取自己的信息
            me = await client.get_me()
            if me is None:
                return True
            
            # 尝试发送消息到源机器人
            await client.send_message(Config.SOURCE_BOT, '🏠主菜单')
            await asyncio.sleep(2)
            msgs = await client.get_messages(Config.SOURCE_BOT, limit=1)
            
            if not msgs:
                return True
            
            return False
            
        except (AuthKeyUnregisteredError, UserDeactivatedBanError):
            return True
        except Exception as e:
            print(f'  [WARN] Check banned error: {e}')
            return False  # 不确定，假设未封
    
    async def scrape_with_account(self, account):
        """使用指定账号抓取商品"""
        print(f'\n[{datetime.now().strftime("%H:%M:%S")}] 使用账号 #{account["id"]}: {account["phone"]}')
        
        # 创建客户端
        client = TelegramClient(
            account['session'],
            Config.API_ID,
            Config.API_HASH
        )
        
        # 非交互式连接（不要求输入手机号/验证码）
        await client.connect()
        
        # 检查是否已登录
        if not await client.is_user_authorized():
            print(f'  ❌ 账号 #{account["id"]} Session失效，请重新登录')
            await client.disconnect()
            raise Exception(f'Account {account["id"]} session expired')
        
        # 检查是否被封
        if await self.check_if_banned(client, account):
            print(f'  ❌ 账号 #{account["id"]} 已被封禁')
            raise BannedException(f'Account {account["id"]} is banned')
        
        # 创建抓取器
        scraper = ProductScraper(client)
        await scraper.start()
        
        # 记录开始时间
        start_time = time.time()
        
        # 抓取商品
        await scraper.scrape_all()
        
        # 记录耗时
        elapsed = time.time() - start_time
        print(f'  ✅ 抓取完成，耗时 {elapsed:.1f} 秒')
        
        await client.disconnect()
        
        return elapsed
    
    async def send_telegram_alert(self, message):
        """发送Telegram告警给管理员（通过账号管理Bot）"""
        try:
            # 使用账号管理Bot发送告警
            from telegram import Bot
            
            # 账号管理Bot Token
            ALERT_BOT_TOKEN = '8680801765:AAH9C4uERN9-14hq7p4kfN1EX2wg744syEc'
            ADMIN_ID = 5991190607
            
            bot = Bot(token=ALERT_BOT_TOKEN)
            await bot.send_message(chat_id=ADMIN_ID, text=message)
            
            print(f'✅ 告警已发送给管理员')
            
        except Exception as e:
            print(f'❌ 发送告警失败: {e}')
            print(f'\n告警内容:\n{message}\n')
    
    async def send_ban_alert(self, account):
        """发送封禁告警"""
        if account['id'] in self.banned_notify_sent:
            return  # 已通知过
        
        active_count = self.count_active_accounts()
        
        message = (
            f"⚠️ 刷新账号封禁警报！\n\n"
            f"账号 #{account['id']}\n"
            f"手机: {account['phone']}\n"
            f"状态: 已被封禁\n"
            f"成功次数: {account['success_count']}\n"
            f"失败次数: {account['fail_count']}\n\n"
            f"剩余可用账号: {active_count}/{len(self.accounts)}\n"
        )
        
        if active_count < 5:
            message += "\n🔴 警告：可用账号少于5个，请尽快补充！"
        
        await self.send_telegram_alert(message)
        self.banned_notify_sent.add(account['id'])
    
    async def send_low_accounts_alert(self):
        """发送可用账号不足告警"""
        if self.low_accounts_notified:
            return
        
        active_count = self.count_active_accounts()
        
        message = (
            f"🔴 可用账号不足警报！\n\n"
            f"当前可用账号: {active_count}/{len(self.accounts)}\n"
            f"警告阈值: 5个\n\n"
            f"请尽快补充新账号！"
        )
        
        await self.send_telegram_alert(message)
        self.low_accounts_notified = True
    
    async def send_critical_alert(self):
        """发送严重告警（所有账号不可用）"""
        message = (
            f"🆘 严重警报：所有刷新账号均不可用！\n\n"
            f"系统无法更新商品库存\n"
            f"请立即检查并补充账号！"
        )
        
        await self.send_telegram_alert(message)
    
    async def run(self):
        """主循环"""
        print('='*60)
        print('🔄 多账号轮换刷新器启动')
        print('='*60)
        
        if not self.accounts:
            print('❌ 无可用账号，请先运行 upload_accounts.py 上传账号')
            return
        
        print(f'📊 账号池状态:')
        print(f'  - 总账号数: {len(self.accounts)}')
        print(f'  - 可用账号: {self.count_active_accounts()}')
        print(f'  - 轮换间隔: {self.rotation_interval} 秒')
        print('='*60)
        
        while True:
            # 获取下一个可用账号
            account = self.get_next_account()
            
            if account is None:
                # 所有账号都不可用
                print('🆘 所有账号均不可用！')
                await self.send_critical_alert()
                await asyncio.sleep(300)  # 等5分钟
                continue
            
            # 检查可用账号数量
            active_count = self.count_active_accounts()
            if active_count < 5:
                await self.send_low_accounts_alert()
            else:
                self.low_accounts_notified = False  # 恢复通知标志
            
            try:
                # 使用该账号抓取
                elapsed = await self.scrape_with_account(account)
                
                # 标记成功
                account['status'] = 'active'
                account['success_count'] += 1
                account['last_used'] = int(time.time())
                
                # 自动调整轮换间隔
                if elapsed > 100 and self.rotation_interval < 120:
                    print(f'  ⚙️ 抓取耗时 {elapsed:.1f}秒，自动将轮换间隔调整为 120 秒')
                    self.rotation_interval = 120
                elif elapsed < 50 and self.rotation_interval > 60:
                    print(f'  ⚙️ 抓取耗时 {elapsed:.1f}秒，可以将轮换间隔调整为 60 秒')
                    self.rotation_interval = 60
                
            except BannedException as e:
                # 账号被封
                account['status'] = 'banned'
                account['banned_at'] = int(time.time())
                account['fail_count'] += 1
                await self.send_ban_alert(account)
                print(f'  ❌ 账号 #{account["id"]} 已被标记为封禁')
            
            except Exception as e:
                # 检查是否是Session失效
                if 'session expired' in str(e).lower():
                    account['status'] = 'failed'
                    print(f'  ⚠️ 账号 #{account["id"]} Session失效，已标记为失败状态')
                    print(f'  💡 提示：可使用账号管理Bot重新添加该账号')
                    print(f'  ⏭️ 自动跳过，使用下一个账号...')
                else:
                    # 其他错误
                    account['fail_count'] += 1
                    print(f'  ❌ 抓取失败: {e}')
                    
                    # 连续失败5次标记为失败状态
                    if account['fail_count'] > 5:
                        account['status'] = 'failed'
                        print(f'  ⚠️ 账号 #{account["id"]} 连续失败，标记为失败状态')
                        print(f'  ⏭️ 自动跳过，使用下一个账号...')
                    else:
                        print(f'  ⏭️ 将在下次轮换时重试...')
            
            # 保存状态
            self.save_config()
            
            # 等待下一次轮换
            await asyncio.sleep(self.rotation_interval)

class BannedException(Exception):
    """账号被封异常"""
    pass

async def main():
    """入口函数"""
    manager = ScraperPoolManager()
    await manager.run()

if __name__ == '__main__':
    asyncio.run(main())
