"""
@SanJianbot 专属购买流程
"""
import asyncio
import os
from telethon import TelegramClient

class SanJianbotPurchaser:
    """@SanJianbot 购买器"""
    
    def __init__(self, client):
        self.client = client
        self.bot = '@SanJianbot'
    
    async def navigate_to_category(self, category):
        """导航到分类"""
        # 1. 点击 🛒 商品分类（@SanJianbot 主菜单就有这个按钮）
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '商品分类' in btn.text or '🛒' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
        
        # 2. 点击分类
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
                        # @SanJianbot 商品名称中可能有emoji
                        if name in btn.text or btn.text.endswith(name):
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
                    if '购买' in btn.text or '🛒' in btn.text:
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
                    # @SanJianbot 用 "确认购买 ✅"
                    if '确认购买' in btn.text or '确认' in btn.text:
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
            
            # @SanJianbot 只发送 1 个 zip 文件
            if len(files) >= 1:
                break
            
            await asyncio.sleep(5)
        
        if not files:
            raise Exception('未收到文件')
        
        return files
    
    async def check_balance(self):
        """检查余额"""
        # @SanJianbot 主菜单显示余额
        msgs = await self.client.get_messages(self.bot, limit=1)
        if msgs and msgs[0].text:
            import re
            match = re.search(r'(?:余额|剩余金额)[：:]\s*(\d+\.?\d*)\s*USDT', msgs[0].text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    async def auto_recharge(self, amount):
        """自动充值"""
        # @SanJianbot 充值流程（需要根据实际情况补充）
        # 暂时抛出异常，提示用户手动充值
        raise Exception(f'@SanJianbot 需要手动充值 {amount} USDT')
