"""
多来源商品同步脚本
支持从多个源机器人同步商品
"""
import asyncio
from telethon import TelegramClient
from config import Config
from database import Database
import re

class MultiSourceScraper:
    """多来源商品同步器"""
    
    def __init__(self):
        self.db = Database()
    
    async def sync_all_sources(self):
        """同步所有商品来源"""
        print('🔄 开始同步所有商品来源...')
        print()
        
        for source in Config.PRODUCT_SOURCES:
            print(f'📱 同步来源: {source["name"]}')
            print(f'   源机器人: {source["source_bot"]}')
            print(f'   Session: {source["session"]}')
            print()
            
            try:
                await self.sync_source(
                    source_name=source['name'],
                    source_bot=source['source_bot'],
                    session_path=source['session']
                )
                print(f'✅ {source["name"]} 同步完成')
            except Exception as e:
                print(f'❌ {source["name"]} 同步失败: {e}')
            
            print()
    
    async def sync_source(self, source_name, source_bot, session_path):
        """同步单个来源的商品"""
        # 创建客户端
        client = TelegramClient(session_path, Config.API_ID, Config.API_HASH)
        
        try:
            await client.start()
            
            # 发送 /start 获取主菜单
            await client.send_message(source_bot, '/start')
            await asyncio.sleep(2)
            
            # 点击"商品分类"或"账号列表"
            msgs = await client.get_messages(source_bot, limit=1)
            if not msgs or not msgs[0].buttons:
                raise Exception('未找到商品入口按钮')
            
            for row in msgs[0].buttons:
                for btn in row:
                    # @SanJianbot 用 "商品分类"，@hao24bot 用 "账号列表"
                    if '商品分类' in btn.text or '账号列表' in btn.text or '🛒' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
            
            # 获取所有分类
            msgs = await client.get_messages(source_bot, limit=1)
            if not msgs or not msgs[0].buttons:
                raise Exception('未找到分类按钮')
            
            categories = []
            for row in msgs[0].buttons:
                for btn in row:
                    if btn.text and btn.text not in ['🏠主菜单', '⬅️ 返回']:
                        categories.append(btn.text.strip())
            
            print(f'   找到 {len(categories)} 个分类: {categories}')
            
            # 遍历每个分类
            total_products = 0
            for category in categories:
                products = await self._scrape_category(client, source_bot, category)
                
                # 保存商品到数据库
                for p in products:
                    self._save_product(
                        source_name=source_name,
                        source_bot=source_bot,
                        buyer_session=session_path,
                        **p
                    )
                
                total_products += len(products)
                print(f'      {category}: {len(products)} 个商品')
            
            print(f'   总计: {total_products} 个商品')
            
        finally:
            await client.disconnect()
    
    async def _scrape_category(self, client, source_bot, category):
        """抓取单个分类的商品"""
        # 返回主菜单
        await client.send_message(source_bot, '/start')
        await asyncio.sleep(2)
        
        # 点击商品分类或账号列表
        msgs = await client.get_messages(source_bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '商品分类' in btn.text or '账号列表' in btn.text or '🛒' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
        
        # 点击分类
        msgs = await client.get_messages(source_bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if category in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
        
        # 获取商品列表
        msgs = await client.get_messages(source_bot, limit=1)
        if not msgs or not msgs[0].buttons:
            return []
        
        products = []
        for row in msgs[0].buttons:
            for btn in row:
                if btn.text and btn.text not in ['🏠主菜单', '⬅️ 返回']:
                    product = self._parse_product(category, btn.text, btn.data)
                    if product:
                        products.append(product)
        
        return products
    
    def _parse_product(self, category, text, button_data):
        """解析商品信息"""
        # @hao24bot 格式: "美国 【100】- $0.15"
        # @SanJianbot 格式: "🇬🇧 德国+49 [1.35U] 数量 (947)"
        
        # 尝试匹配 @hao24bot 格式
        match = re.search(r'(.+?)\s*【(\d+)】.*?\$(\d+\.?\d*)', text)
        if match:
            name = match.group(1).strip()
            stock = int(match.group(2))
            price = float(match.group(3))
        else:
            # 尝试匹配 @SanJianbot 格式
            match = re.search(r'(.+?)\s*\[(\d+\.?\d*)U\]\s*数量\s*\((\d+)\)', text)
            if not match:
                return None
            
            name = match.group(1).strip()
            # 移除emoji（如 🇬🇧）
            name = re.sub(r'[\U0001F1E6-\U0001F1FF]+', '', name).strip()
            price = float(match.group(2))
            stock = int(match.group(3))
        
        # 计算售价
        selling_price = round(price + Config.MARKUP_FIXED, 2)
        if selling_price - price < Config.MIN_PROFIT:
            selling_price = round(price + Config.MIN_PROFIT, 2)
        
        return {
            'category': category,
            'name': name,
            'original_price': price,
            'selling_price': selling_price,
            'stock': stock,
            'button_data': button_data.decode() if button_data else None
        }
    
    def _save_product(self, source_name, source_bot, buyer_session, category, name, 
                     original_price, selling_price, stock, button_data):
        """保存商品到数据库"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # 生成唯一ID
        source_product_id = f'{source_bot}_{category}_{name}'
        
        # 插入或更新
        c.execute('''
            INSERT INTO products (
                source_product_id, source_name, source_bot, buyer_session,
                category, name, original_price, selling_price, stock, button_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_product_id) DO UPDATE SET
                stock = excluded.stock,
                original_price = excluded.original_price,
                selling_price = excluded.selling_price,
                last_updated = CURRENT_TIMESTAMP
        ''', (
            source_product_id, source_name, source_bot, buyer_session,
            category, name, original_price, selling_price, stock, button_data
        ))
        
        conn.commit()
        conn.close()

async def main():
    """主函数"""
    scraper = MultiSourceScraper()
    await scraper.sync_all_sources()
    print()
    print('✅ 所有来源同步完成！')

if __name__ == '__main__':
    asyncio.run(main())
