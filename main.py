"""
主程序
"""
import asyncio
import sys
from scraper import ProductScraper
from purchaser import AutoPurchaser
from bot import SalesBot
from database import Database
from config import Config

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

async def sync_products_loop(scraper):
    """商品同步循环"""
    while True:
        try:
            print(f'\n📊 开始同步商品...')
            await scraper.scrape_all()
            print(f'✅ 同步完成，等待 {Config.SYNC_INTERVAL} 秒后再次同步\n')
        except Exception as e:
            print(f'❌ 同步失败: {e}')
        
        await asyncio.sleep(Config.SYNC_INTERVAL)

async def main():
    """主函数"""
    print('='*60)
    print('🤖 Telegram 账号代购销售系统')
    print('='*60)
    
    # 初始化数据库
    db = Database()
    
    # 登录代购账号（只登录一次）
    from client_manager import ClientManager
    buyer_client = await ClientManager.get_client()
    
    # 初始化代购模块（共享客户端）
    purchaser = AutoPurchaser(buyer_client)
    await purchaser.start()
    
    # 初始化商品抓取器（共享客户端）
    scraper = ProductScraper(buyer_client)
    await scraper.start()
    
    # 首次同步商品
    try:
        await scraper.scrape_all()
    except Exception as e:
        print(f'⚠️ 首次同步失败: {e}')
    
    # 启动定时同步（后台任务）
    asyncio.create_task(sync_products_loop(scraper))
    
    # 启动销售机器人（阻塞）
    sales_bot = SalesBot(purchaser)
    
    print('\n✅ 系统启动完成！')
    print('='*60)
    
    # 机器人会阻塞在这里
    sales_bot.start_bot()

if __name__ == '__main__':
    asyncio.run(main())
