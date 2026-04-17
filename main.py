"""
主程序（代购版 - 不参与商品抓取）
商品抓取由独立的 scraper_pool_manager.py 负责
"""
import asyncio
import sys
# from scraper import ProductScraper  # 不再需要
from purchaser import AutoPurchaser
from bot import SalesBot
from database import Database
# from config import Config  # 不再需要同步间隔

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """主函数"""
    print('='*60)
    print('🤖 Telegram 账号代购销售系统（代购版）')
    print('='*60)
    print('💡 商品抓取由独立的 scraper_pool_manager.py 负责')
    print('💡 本程序只负责购买和销售')
    print('='*60)
    
    # 初始化数据库
    db = Database()
    
    # 登录代购账号（只登录一次）
    from client_manager import ClientManager
    buyer_client = await ClientManager.get_client()
    
    # 初始化代购模块（共享客户端）
    purchaser = AutoPurchaser(buyer_client)
    await purchaser.start()
    
    # ❌ 不再初始化商品抓取器
    # scraper = ProductScraper(buyer_client)
    # await scraper.start()
    
    # 检查数据库中是否有商品
    conn = db.get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
    product_count = c.fetchone()[0]
    conn.close()
    
    if product_count > 0:
        print(f'✅ 检测到 {product_count} 个商品')
    else:
        print('⚠️ 数据库中暂无商品')
        print('💡 请确保 scraper_pool_manager.py 正在运行')
    
    # ❌ 不再启动定时同步
    # asyncio.create_task(sync_products_loop(scraper))
    
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
