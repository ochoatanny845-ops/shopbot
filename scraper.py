"""
商品抓取模块
"""
import asyncio
import os
import re
from datetime import datetime
from telethon import TelegramClient
from config import Config
from database import Database

class ProductScraper:
    """商品抓取器"""
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.client = None
    
    async def start(self):
        """启动客户端（智能登录）"""
        self.client = TelegramClient(
            Config.BUYER_SESSION,
            Config.API_ID,
            Config.API_HASH
        )
        
        # 检测 Session 是否存在
        session_file = Config.BUYER_SESSION + '.session'
        if os.path.exists(session_file):
            print('🔍 检测到 Session 文件，尝试自动登录...')
            try:
                # 尝试使用 Session 自动登录
                await self.client.start(password=lambda: Config.BUYER_2FA or None)
                me = await self.client.get_me()
                print(f'✅ 代购账号登录成功: {me.first_name} ({me.phone})')
                return
            except Exception as e:
                print(f'⚠️ Session 失效: {e}')
                print('📞 需要重新登录...\n')
        
        # 首次登录或 Session 失效
        print('='*60)
        print('📱 首次登录 - 需要手机号和验证码')
        print('='*60)
        
        phone = input('请输入手机号（带国家代码，如 +8613800138000）: ').strip()
        
        # 定义密码函数
        def get_password():
            if Config.BUYER_2FA:
                return Config.BUYER_2FA
            return input('请输入两步验证密码（如果没有请直接回车）: ').strip() or None
        
        await self.client.start(
            phone=phone,
            password=get_password
        )
        
        me = await self.client.get_me()
        print(f'\n✅ 登录成功！')
        print(f'   账号: {me.first_name}')
        print(f'   手机: {me.phone}')
        print(f'   Session 已保存到: {session_file}')
        print('='*60 + '\n')
    
    async def scrape_all(self):
        """抓取所有商品"""
        print(f'📊 开始抓取商品...')
        
        try:
            # 发送 /start
            await self.client.send_message(Config.SOURCE_BOT, '/start')
            await asyncio.sleep(2)
            
            # 点击"账号列表"
            msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
            if msgs and msgs[0].buttons:
                for row in msgs[0].buttons:
                    for btn in row:
                        if '账号列表' in btn.text or '🛒' in btn.text:
                            await btn.click()
                            await asyncio.sleep(2)
                            break
            
            # 获取分类列表
            categories = await self._get_categories()
            print(f'✅ 找到 {len(categories)} 个分类')
            
            # 抓取每个分类的商品
            all_products = []
            for category in categories:
                products = await self._scrape_category(category)
                all_products.extend(products)
                print(f'  ✅ {category}: {len(products)} 个商品')
                await asyncio.sleep(Config.REQUEST_DELAY)
            
            # 保存到数据库
            self._save_products(all_products)
            
            print(f'✅ 总共抓取 {len(all_products)} 个商品')
            return all_products
            
        except Exception as e:
            print(f'❌ 抓取失败: {e}')
            raise
    
    async def _get_categories(self):
        """获取分类列表"""
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        categories = []
        
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    text = btn.text
                    # 跳过返回按钮等
                    if '返回' in text or '搜索' in text:
                        continue
                    # 包含"可用数量"的是分类
                    if '可用数量' in text:
                        # 清理分类名称
                        clean = re.sub(r'\s*可用数量【\d+】', '', text).strip()
                        categories.append(clean)
        
        return categories
    
    async def _scrape_category(self, category):
        """抓取某个分类的商品"""
        # 返回分类列表页
        await self._go_back()
        
        # 点击分类
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        clicked = False
        
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if category in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        clicked = True
                        break
                if clicked:
                    break
        
        if not clicked:
            return []
        
        # 抓取商品（支持翻页，最多3页）
        products = []
        for page in range(1, 4):
            msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
            
            if not msgs or not msgs[0].buttons:
                break
            
            page_products = []
            has_next = False
            
            for row in msgs[0].buttons:
                for btn in row:
                    text = btn.text
                    
                    # 检测下一页
                    if '下一页' in text or text.strip() == '➡️':
                        has_next = True
                        continue
                    
                    # 跳过控制按钮
                    if any(x in text for x in ['返回', '上一页', '⬅️', '↩️', '页面']):
                        continue
                    
                    # 解析商品
                    product = self._parse_product(text, category)
                    if product:
                        page_products.append(product)
            
            products.extend(page_products)
            
            # 检测循环
            if page > 1 and len(page_products) > 0:
                # 简单检测：如果这页商品数为0，停止
                pass
            
            if not has_next:
                break
            
            # 点击下一页
            if has_next:
                for row in msgs[0].buttons:
                    for btn in row:
                        if '下一页' in btn.text or btn.text.strip() == '➡️':
                            await btn.click()
                            await asyncio.sleep(1.5)
                            break
        
        return products
    
    def _parse_product(self, text, category):
        """解析商品按钮"""
        # 格式：🇲🇲+95缅甸【27001】- $0.33
        match = re.match(r'(.+?)【(\d+)】\s*-\s*\$?([\d.]+)', text)
        
        if match:
            name = match.group(1).strip()
            stock = int(match.group(2))
            original_price = float(match.group(3))
            
            # 计算售价
            selling_price = original_price + Config.MARKUP_FIXED
            if selling_price - original_price < Config.MIN_PROFIT:
                selling_price = original_price + Config.MIN_PROFIT
            
            return {
                'category': category,
                'name': name,
                'stock': stock,
                'original_price': original_price,
                'selling_price': round(selling_price, 2),
                'button_data': text
            }
        
        return None
    
    async def _go_back(self):
        """返回分类列表页"""
        for _ in range(3):
            msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
            
            if not msgs or not msgs[0].buttons:
                break
            
            # 检查是否已经在分类列表页
            category_count = 0
            for row in msgs[0].buttons:
                for btn in row:
                    if '可用数量' in btn.text:
                        category_count += 1
            
            if category_count >= 3:
                break
            
            # 点击返回
            for row in msgs[0].buttons:
                for btn in row:
                    if '返回' in btn.text or '↩️' in btn.text:
                        await btn.click()
                        await asyncio.sleep(1)
                        break
    
    def _save_products(self, products):
        """保存商品到数据库"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        for p in products:
            # 生成唯一ID
            unique_id = f"{p['category']}:{p['name']}"
            
            c.execute('''
                INSERT OR REPLACE INTO products 
                (source_product_id, category, name, original_price, selling_price, 
                 stock, button_data, last_updated, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (
                unique_id,
                p['category'],
                p['name'],
                p['original_price'],
                p['selling_price'],
                p['stock'],
                p['button_data'],
                datetime.now()
            ))
        
        conn.commit()
        conn.close()
        print(f'✅ 保存了 {len(products)} 个商品到数据库')
    
    async def stop(self):
        """停止客户端"""
        if self.client:
            await self.client.disconnect()
