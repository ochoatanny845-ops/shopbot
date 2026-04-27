"""
库存定时同步管理器
- 固定账号每5分钟同步一次库存
- 账号失败时自动切换到下一个
- 自动检测封禁并告警
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
    """库存同步管理器"""
    
    def __init__(self, config_file='accounts_pool.json'):
        self.config_file = config_file
        self.accounts = []
        self.current_account_index = 0
        self.sync_interval = 300  # 5分钟同步一次
        self.banned_notify_sent = set()
        self.low_accounts_notified = False
        self.load_config()
    
    def load_config(self):
        """加载账号配置"""
        if not os.path.exists(self.config_file):
            print(f'⚠️ 配置文件不存在: {self.config_file}')
            print(f'💡 脚本启动时会自动初始化账号池')
            self.accounts = []
            return
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.accounts = data.get('accounts', [])
            self.current_account_index = data.get('current_index', 0)
            # 兼容旧配置：如果有 rotation_interval，忽略它
            if 'sync_interval' in data:
                self.sync_interval = data['sync_interval']
        
        print(f'✅ 加载了 {len(self.accounts)} 个账号')
        print(f'⏱️ 同步间隔: {self.sync_interval} 秒 ({self.sync_interval // 60} 分钟)')
    
    def save_config(self):
        """保存账号状态"""
        data = {
            'accounts': self.accounts,
            'current_index': self.current_account_index,
            'sync_interval': self.sync_interval
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_current_account(self):
        """获取当前使用的账号（失败时自动切换）"""
        if not self.accounts:
            return None
        
        # 确保索引不越界
        if self.current_account_index >= len(self.accounts):
            self.current_account_index = 0
        
        # 尝试找到一个可用账号
        tried = 0
        while tried < len(self.accounts):
            account = self.accounts[self.current_account_index]
            
            if account['status'] == 'active':
                return account
            
            # 当前账号不可用，尝试下一个
            self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
            tried += 1
        
        return None  # 所有账号都不可用
    
    def switch_to_next_account(self):
        """切换到下一个账号"""
        self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
        print(f'  🔄 切换到下一个账号 (索引: {self.current_account_index})')
    
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
        
        # 非交互式连接
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
        stats = await scraper.scrape_all()
        
        # 记录耗时
        elapsed = time.time() - start_time
        print(f'  ✅ 抓取完成，耗时 {elapsed:.1f} 秒')
        
        await client.disconnect()
        
        # 返回统计信息
        return {
            'elapsed': elapsed,
            'total_products': stats.get('total_products', 0),
            'total_categories': stats.get('total_categories', 0),
            'total_stock': stats.get('total_stock', 0)
        }
    
    async def send_telegram_alert(self, message):
        """发送Telegram告警给管理员"""
        try:
            from telegram import Bot
            
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
            return
        
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
        """发送严重告警"""
        message = (
            f"🆘 严重警报：所有刷新账号均不可用！\n\n"
            f"系统无法更新商品库存\n"
            f"请立即检查并补充账号！"
        )
        
        await self.send_telegram_alert(message)
    
    async def send_stock_update_notification(self, account, elapsed, total_products, total_categories, total_stock):
        """发送库存更新通知"""
        try:
            from datetime import datetime, timedelta
            now = datetime.now()
            next_update = now + timedelta(seconds=self.sync_interval)
            
            message = (
                f"✅ 库存已更新！\n\n"
                f"🕐 更新时间: {now.strftime('%H:%M:%S')}\n"
                f"📦 总商品数: {total_products}\n"
                f"📊 分类数: {total_categories}\n"
                f"🏪 总库存: {total_stock:,}\n"
                f"⏱️ 耗时: {elapsed:.1f} 秒\n"
                f"🔄 下次更新: {next_update.strftime('%H:%M:%S')} ({self.sync_interval // 60} 分钟后)\n\n"
                f"使用账号: #{account['id']} ({account['phone']})"
            )
            
            await self.send_telegram_alert(message)
            print(f'  📢 已发送库存更新通知')
            
        except Exception as e:
            print(f'  ⚠️ 发送更新通知失败: {e}')
    
    async def run(self):
        """主循环 - 每5分钟同步一次"""
        print('='*60)
        print('🔄 库存定时同步器启动')
        print('='*60)
        
        if not self.accounts:
            print('❌ 账号池为空，脚本启动时会自动初始化')
            print('💡 如果持续为空，请检查账号初始化逻辑')
            return
        
        print(f'📊 账号池状态:')
        print(f'  - 总账号数: {len(self.accounts)}')
        print(f'  - 可用账号: {self.count_active_accounts()}')
        print(f'  - 同步间隔: {self.sync_interval} 秒 ({self.sync_interval // 60} 分钟)')
        print('='*60)
        
        while True:
            # 获取当前账号
            account = self.get_current_account()
            
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
                self.low_accounts_notified = False
            
            try:
                # 使用该账号抓取
                result = await self.scrape_with_account(account)
                
                # 提取数据
                elapsed = result['elapsed']
                total_products = result['total_products']
                total_categories = result['total_categories']
                total_stock = result['total_stock']
                
                # 标记成功
                account['status'] = 'active'
                account['success_count'] += 1
                account['last_used'] = int(time.time())
                
                # 发送更新通知
                await self.send_stock_update_notification(account, elapsed, total_products, total_categories, total_stock)
                
            except BannedException as e:
                # 账号被封，切换到下一个
                account['status'] = 'banned'
                account['banned_at'] = int(time.time())
                account['fail_count'] += 1
                await self.send_ban_alert(account)
                print(f'  ❌ 账号 #{account["id"]} 已被标记为封禁')
                self.switch_to_next_account()
            
            except Exception as e:
                # 其他错误
                if 'session expired' in str(e).lower():
                    account['status'] = 'failed'
                    print(f'  ⚠️ 账号 #{account["id"]} Session失效，已标记为失败状态')
                    print(f'  💡 提示：可使用账号管理Bot重新添加该账号')
                    self.switch_to_next_account()
                else:
                    account['fail_count'] += 1
                    print(f'  ❌ 抓取失败: {e}')
                    
                    # 连续失败5次切换账号
                    if account['fail_count'] > 5:
                        account['status'] = 'failed'
                        print(f'  ⚠️ 账号 #{account["id"]} 连续失败，标记为失败状态')
                        self.switch_to_next_account()
            
            # 保存状态
            self.save_config()
            
            # 等待5分钟后下次同步
            print(f'\n⏰ 等待 {self.sync_interval} 秒 ({self.sync_interval // 60} 分钟) 后进行下次同步...')
            await asyncio.sleep(self.sync_interval)

class BannedException(Exception):
    """账号被封异常"""
    pass

async def main():
    """入口函数"""
    manager = ScraperPoolManager()
    await manager.run()

if __name__ == '__main__':
    asyncio.run(main())
