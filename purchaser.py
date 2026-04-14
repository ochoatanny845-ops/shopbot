"""
自动代购模块
"""
import asyncio
import os
import zipfile
from datetime import datetime
from telethon import TelegramClient
from config import Config
from database import Database

class AutoPurchaser:
    """自动代购器"""
    
    def __init__(self):
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
            print('🔍 代购模块：检测到 Session 文件，尝试自动登录...')
            try:
                # 尝试使用 Session 自动登录
                await self.client.start(password=lambda: Config.BUYER_2FA or None)
                me = await self.client.get_me()
                print(f'✅ 代购客户端启动: {me.first_name} ({me.phone})')
                return
            except Exception as e:
                print(f'⚠️ Session 失效: {e}')
                print('📞 需要重新登录...\n')
        
        # 首次登录或 Session 失效
        print('='*60)
        print('📱 代购模块登录 - 需要手机号和验证码')
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
    
    async def purchase(self, product_id):
        """
        购买商品
        
        Returns:
            str: ZIP文件路径
        """
        # 查询商品信息
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT name, category, original_price
            FROM products
            WHERE id = ? AND is_active = 1
        ''', (product_id,))
        
        product = c.fetchone()
        conn.close()
        
        if not product:
            raise Exception('商品不存在')
        
        name, category, price = product
        
        print(f'📦 开始代购: {name}')
        
        try:
            # 1. 导航到分类
            await self._navigate_to_category(category)
            
            # 2. 查找并点击商品
            await self._click_product(name)
            
            # 3. 点击购买
            await self._click_buy()
            
            # 4. 输入数量
            await self._input_quantity(1)
            
            # 5. 确认购买
            await self._confirm_purchase()
            
            # 6. 等待并接收文件
            files = await self._wait_for_files()
            
            # 7. 压缩文件
            zip_path = self._zip_files(files, product_id)
            
            print(f'✅ 代购成功: {zip_path}')
            return zip_path
            
        except Exception as e:
            print(f'❌ 代购失败: {e}')
            raise
    
    async def _navigate_to_category(self, category):
        """导航到分类"""
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
        
        # 点击分类
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if category in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        return
        
        raise Exception(f'未找到分类: {category}')
    
    async def _click_product(self, product_name):
        """点击商品"""
        # 提取商品核心名称（去掉库存和价格）
        import re
        core_name = re.sub(r'【\d+】.*', '', product_name).strip()
        
        # 最多翻3页查找
        for page in range(3):
            msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
            
            if not msgs or not msgs[0].buttons:
                break
            
            # 查找商品
            for row in msgs[0].buttons:
                for btn in row:
                    if core_name in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        return
            
            # 翻页
            has_next = False
            for row in msgs[0].buttons:
                for btn in row:
                    if '下一页' in btn.text or btn.text.strip() == '➡️':
                        await btn.click()
                        await asyncio.sleep(1.5)
                        has_next = True
                        break
                if has_next:
                    break
            
            if not has_next:
                break
        
        raise Exception(f'未找到商品: {product_name}')
    
    async def _click_buy(self):
        """点击购买按钮"""
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '立即购买' in btn.text or '购买' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        return
        
        raise Exception('未找到购买按钮')
    
    async def _input_quantity(self, quantity):
        """输入购买数量"""
        await self.client.send_message(Config.SOURCE_BOT, str(quantity))
        await asyncio.sleep(2)
    
    async def _confirm_purchase(self):
        """确认购买"""
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for btn in row:
                    if '确定购买' in btn.text or '确认购买' in btn.text or ('确认' in btn.text and '✅' in btn.text):
                        await btn.click()
                        await asyncio.sleep(3)
                        return
        
        raise Exception('未找到确认按钮')
    
    async def _wait_for_files(self):
        """等待并接收文件"""
        print('⏳ 等待文件...')
        
        files = []
        start_time = asyncio.get_event_loop().time()
        timeout = 60  # 60秒超时
        
        while len(files) < 3:
            # 检查超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise Exception('接收文件超时')
            
            # 获取最新消息
            msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=10)
            
            for msg in msgs:
                if msg.document and msg.id not in [f['msg_id'] for f in files]:
                    # 获取文件信息
                    file_name = msg.file.name or f'file_{len(files) + 1}'
                    file_ext = msg.file.ext or ''
                    
                    # 下载文件
                    file_path = await msg.download_media(file=Config.ORDER_FILES_DIR)
                    
                    files.append({
                        'msg_id': msg.id,
                        'path': file_path,
                        'name': file_name,
                        'ext': file_ext,
                        'size': msg.file.size
                    })
                    
                    # 显示文件类型
                    file_type = '📄 TXT' if file_ext == '.txt' else '📦 ZIP' if file_ext == '.zip' else '📁 文件'
                    print(f'  ✅ {file_type} 接收 {len(files)}/3: {file_name} ({msg.file.size} bytes)')
                    
                    if len(files) >= 3:
                        break
            
            await asyncio.sleep(2)
        
        return files
    
    def _zip_files(self, files, product_id):
        """压缩文件"""
        # 创建输出目录
        os.makedirs(Config.ORDER_FILES_DIR, exist_ok=True)
        
        # 生成ZIP文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'order_{product_id}_{timestamp}.zip'
        zip_path = os.path.join(Config.ORDER_FILES_DIR, zip_filename)
        
        # 压缩所有文件（包括 .txt 和 .zip）
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in files:
                # 保留原始文件名和扩展名
                arcname = f['name']
                
                # 如果没有扩展名，根据内容判断
                if not arcname or arcname == f'file_{len(files)}.txt':
                    # 从路径中提取文件名
                    arcname = os.path.basename(f['path'])
                
                zipf.write(f['path'], arcname)
                print(f'  📦 添加到ZIP: {arcname}')
        
        # 删除临时文件
        for f in files:
            try:
                os.remove(f['path'])
            except Exception as e:
                print(f'  ⚠️ 删除临时文件失败: {e}')
        
        print(f'✅ ZIP文件创建成功: {zip_path}')
        return zip_path
    
    async def stop(self):
        """停止客户端"""
        if self.client:
            await self.client.disconnect()
