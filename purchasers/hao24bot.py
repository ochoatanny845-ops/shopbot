"""
@hao24bot 专属购买流程
"""
import asyncio
import os
from telethon import TelegramClient

class Hao24BotPurchaser:
    """@hao24bot 购买器"""
    
    def __init__(self, client):
        self.client = client
        self.bot = '@hao24bot'
    
    async def navigate_to_category(self, category):
        """导航到分类"""
        # 1. 发送 🏠主菜单
        await self.client.send_message(self.bot, '🏠主菜单')
        await asyncio.sleep(2)
        
        # 2. 点击"账号列表"
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '账号列表' in btn.text or '🛒' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
        
        # 3. 点击分类
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if category in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        return
        
        raise Exception(f'未找到分类: {category}')
    
    async def click_product(self, name):
        """点击商品"""
        max_attempts = 3
        for attempt in range(max_attempts):
            msgs = await self.client.get_messages(self.bot, limit=1)
            if msgs and msgs[0].buttons:
                for row in msgs[0].buttons:
                    for btn in row:
                        if name in btn.text:
                            await btn.click()
                            await asyncio.sleep(2)
                            return
            
            if attempt < max_attempts - 1:
                await asyncio.sleep(1)
        
        raise Exception(f'未找到商品: {name}')
    
    async def click_buy(self):
        """点击购买按钮"""
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '购买' in btn.text or '💰' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        return
        raise Exception('未找到购买按钮')
    
    async def input_quantity(self, quantity):
        """输入购买数量"""
        await self.client.send_message(self.bot, str(quantity))
        await asyncio.sleep(2)
    
    async def confirm_purchase(self):
        """确认购买"""
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '确认' in btn.text or '✅' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        return
        raise Exception('未找到确认按钮')
    
    async def wait_for_files(self, after_msg_id, save_dir, timeout=180):
        """等待并接收文件"""
        files = []
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            msgs = await self.client.get_messages(self.bot, limit=10)
            
            for msg in msgs:
                if msg.id <= after_msg_id:
                    continue
                
                if msg.media and hasattr(msg.media, 'document'):
                    filename = msg.file.name or f'file_{msg.id}'
                    
                    # 跳过视频
                    if filename.endswith('.mp4'):
                        continue
                    
                    # 只接收 .txt 和 .zip
                    if not (filename.endswith('.txt') or filename.endswith('.zip')):
                        continue
                    
                    filepath = os.path.join(save_dir, filename)
                    
                    # 避免重复下载
                    if any(f['path'] == filepath for f in files):
                        continue
                    
                    await self.client.download_media(msg, filepath)
                    files.append({'path': filepath, 'name': filename})
            
            # @hao24bot 发送 3 个文件
            if len(files) >= 3:
                break
            
            await asyncio.sleep(5)
        
        if not files:
            raise Exception('未收到文件')
        
        return files
    
    async def check_balance(self):
        """检查余额"""
        await self.client.send_message(self.bot, '🏠主菜单')
        await asyncio.sleep(2)
        
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].text:
            import re
            match = re.search(r'余额[：:]\s*\$?(\d+\.?\d*)', msgs[0].text)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    async def auto_recharge(self, amount):
        """自动充值"""
        await self.client.send_message(self.bot, '🏠主菜单')
        await asyncio.sleep(2)
        
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '充值' in btn.text or '💰' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
        
        await self.client.send_message(self.bot, str(amount))
        await asyncio.sleep(2)
        
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '确认' in btn.text or '✅' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
        
        print(f'💰 等待充值到账...')
        await asyncio.sleep(120)
        
        balance = await self.check_balance()
        print(f'✅ 充值后余额: ${balance:.2f}')
