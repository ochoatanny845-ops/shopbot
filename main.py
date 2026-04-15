"""
主程序
"""
import asyncio
import sys
from purchaser import AutoPurchaser
from bot import SalesBot
from database import Database
from config import Config

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

async def sync_products_loop():
    """商品同步循环（使用多来源同步）"""
    # 先等待，再同步
    await asyncio.sleep(Config.SYNC_INTERVAL)
    
    while True:
        try:
            print(f'\n🔄 开始定时同步商品（多来源）...')
            from sync_multi_source import MultiSourceScraper
            scraper = MultiSourceScraper()
            await scraper.sync_all_sources()
            print(f'✅ 定时同步完成，下次同步时间: {Config.SYNC_INTERVAL // 60} 分钟后\n')
        except Exception as e:
            print(f'❌ 定时同步失败: {e}')
        
        await asyncio.sleep(Config.SYNC_INTERVAL)

async def main():
    """主函数"""
    print('='*60)
    print('🤖 Telegram 账号代购销售系统')
    print('='*60)
    
    # 初始化数据库
    db = Database()
    
    # 登录代购账号1（只登录一次，用于主机器人功能）
    from client_manager import ClientManager
    buyer_client = await ClientManager.get_client()
    
    # 初始化代购模块（共享客户端）
    purchaser = AutoPurchaser(buyer_client)
    await purchaser.start()
    
    print('✅ 代购模块已准备就绪')
    
    # 检查数据库中是否有商品
    conn = db.get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
    product_count = c.fetchone()[0]
    conn.close()
    
    if product_count > 0:
        print(f'✅ 检测到 {product_count} 个商品，跳过首次同步')
        print(f'⏰ 将在 {Config.SYNC_INTERVAL // 60} 分钟后自动同步')
    else:
        print('📊 首次启动，开始抓取商品（多来源）...')
        try:
            from sync_multi_source import MultiSourceScraper
            scraper = MultiSourceScraper()
            await scraper.sync_all_sources()
        except Exception as e:
            print(f'⚠️ 首次同步失败: {e}')
    
    # 启动定时同步（60分钟后开始）
    asyncio.create_task(sync_products_loop())
    
    # 启动销售机器人（异步方式）
    sales_bot = SalesBot(purchaser)
    await sales_bot.start()
    
    print('\n✅ 系统启动完成！')
    print('='*60)
    print('💡 按 Ctrl+C 退出系统')
    print('='*60)
    
    # 保持运行
    try:
        await asyncio.Event().wait()  # 永久等待，直到收到停止信号
    except KeyboardInterrupt:
        print('\n⚠️ 正在关闭系统...')
        await sales_bot.stop()
        await ClientManager.disconnect()
        print('✅ 系统已关闭')

if __name__ == '__main__':
    asyncio.run(main())
