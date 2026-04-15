"""
多来源商品同步脚本
支持从多个源机器人同步商品
"""
import asyncio
from telethon import TelegramClient
from config import Config
from database import Database
from purchasers import PurchaserFactory
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
            # 🔧 临时：只同步 @SanJianbot
            if source['source_bot'] != '@SanJianbot':
                print(f'⏭️ 跳过来源: {source["name"]}')
                print()
                continue
            
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
            
            # 🎯 创建对应的购买器（用于导航）
            purchaser = PurchaserFactory.create(source_bot, client)
            
            # 获取分类列表
            categories = await self._get_categories(client, source_bot, purchaser)
            print(f'   找到 {len(categories)} 个分类')
            
            # 遍历每个分类
            total_products = 0
            for category in categories:
                try:
                    products = await self._scrape_category(client, source_bot, purchaser, category)
                    
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
                except Exception as e:
                    print(f'      {category}: 抓取失败 - {e}')
            
            print(f'   总计: {total_products} 个商品')
            
        finally:
            await client.disconnect()
    
    async def _get_categories(self, client, source_bot, purchaser):
        """获取分类列表（使用购买器导航）"""
        # @hao24bot: 发送 🏠主菜单 → 点击"账号列表"
        # @SanJianbot: 发送 🏠主菜单 → 点击 🛒 商品分类
        
        # 首次同步：发送 🏠主菜单
        await client.send_message(source_bot, '🏠主菜单')
        await asyncio.sleep(2)
        
        if source_bot == '@hao24bot':
            # 点击"账号列表"
            msgs = await client.get_messages(source_bot, limit=1)
            if msgs and msgs[0].buttons:
                for row in msgs[0].buttons:
                    for btn in row:
                        if '账号列表' in btn.text or '🛒' in btn.text:
                            await btn.click()
                            await asyncio.sleep(2)
                            break
        
        elif source_bot == '@SanJianbot':
            # 点击 🛒 商品分类
            msgs = await client.get_messages(source_bot, limit=1)
            if msgs and msgs[0].buttons:
                for row in msgs[0].buttons:
                    for btn in row:
                        if '商品分类' in btn.text or '🛒' in btn.text:
                            await btn.click()
                            await asyncio.sleep(2)
                            break
        
        # 获取分类按钮（分类列表页面）
        msgs = await client.get_messages(source_bot, limit=1)
        if not msgs or not msgs[0].buttons:
            return []
        
        categories = []
        for row in msgs[0].buttons:
            for btn in row:
                # 过滤掉底部按钮（主菜单、返回等）
                if btn.text and btn.text not in ['🏠主菜单', '🏠 主菜单', '⬅️ 返回', '↩️返回']:
                    # @SanJianbot 的分类按钮格式：Tdata直登号、Tdata直登号(3-8月) 等
                    # @hao24bot 的分类按钮格式：🌏 亚洲国家 可用数量【64494】等
                    # 排除包含emoji国旗的商品按钮（🇺🇿、🇨🇴等）
                    if not any(char in btn.text for char in ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']):
                        categories.append(btn.text.strip())
        
        return categories
    
    async def _scrape_category(self, client, source_bot, purchaser, category):
        """抓取单个分类的商品"""
        # 点击分类按钮（假设当前在分类列表页面）
        msgs = await client.get_messages(source_bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if category in btn.text:
                        await btn.click()
                        await asyncio.sleep(3)  # 等待页面加载
                        break
        
        # 获取商品列表
        msgs = await client.get_messages(source_bot, limit=1)
        if not msgs or not msgs[0].buttons:
            print(f'         ⚠️ 未找到按钮')
            return []
        
        # 🔍 调试：打印所有按钮
        print(f'         📋 页面按钮：')
        for row in msgs[0].buttons:
            for btn in row:
                print(f'            - {btn.text}')
        
        products = []
        for row in msgs[0].buttons:
            for btn in row:
                if btn.text and btn.text not in ['🏠主菜单', '🏠 主菜单', '⬅️ 返回', '↩️返回', '🔄 返回分类']:
                    product = self._parse_product(category, btn.text, btn.data)
                    if product:
                        products.append(product)
                    else:
                        print(f'         ⚠️ 无法解析: {btn.text}')
        
        # 点击返回按钮回到分类列表
        msgs = await client.get_messages(source_bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    # @hao24bot 用 "返回" 或 "⬅️ 返回"
                    # @SanJianbot 用 "🔄 返回分类"
                    if '返回' in btn.text and '🏠' not in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
        
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
            # 格式：🇨🇦 加拿大+1 [0.33U] 数量 (965)
            match = re.search(r'(.+?)\s+\[(\d+\.?\d*)U\]\s+数量\s*\((\d+)\)', text)
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
