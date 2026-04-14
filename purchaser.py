"""
自动代购模块
"""
import asyncio
import os
from datetime import datetime
from telethon import TelegramClient
from config import Config
from database import Database

class AutoPurchaser:
    """自动代购器"""
    
    # 全局锁：确保同一时间只处理一个订单
    _purchase_lock = asyncio.Lock()
    
    # 余额预警阈值
    BALANCE_WARNING_THRESHOLD = 20.0  # USDT
    
    def __init__(self, client=None):
        self.db = Database()
        self.client = client  # 接收外部传入的客户端
    
    async def start(self):
        """启动客户端（如果没有传入）"""
        if self.client is None:
            from client_manager import ClientManager
            self.client = await ClientManager.get_client()
        print('✅ 代购模块已准备就绪')
    
    async def notify_admin(self, message):
        """通知管理员"""
        try:
            for admin_id in Config.ADMIN_IDS:
                await self.client.send_message(admin_id, message)
                print(f'✅ 已通知管理员 {admin_id}')
        except Exception as e:
            print(f'⚠️ 通知管理员失败: {e}')
    
    async def purchase(self, product_id, quantity=1, user_id=None, order_id=None):
        """
        购买商品（串行处理，确保订单不混淆）
        
        Args:
            product_id: 商品ID
            quantity: 购买数量
            user_id: 用户ID（用于创建隔离目录）
            order_id: 订单ID（用于目录命名）
        
        Returns:
            list: 文件列表 [{'path': ..., 'name': ...}, ...]
        """
        # 🔒 全局锁：同一时间只处理一个订单
        async with AutoPurchaser._purchase_lock:
            print(f'🔒 订单 #{order_id} (用户 {user_id}) 开始处理...')
            
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
            
            print(f'📦 开始代购: {name} (数量: {quantity})')
            
            try:
                # 创建用户专属目录
                user_dir = os.path.join(Config.ORDER_FILES_DIR, str(user_id), f'order_{order_id}')
                os.makedirs(user_dir, exist_ok=True)
                print(f'📁 文件保存路径: {user_dir}')
                
                # ✅ 检查余额并自动充值
                balance = await self.check_balance()
                required_amount = price * quantity
                
                # 检查源机器人余额预警
                if balance < self.BALANCE_WARNING_THRESHOLD:
                    await self.notify_admin(
                        '⚠️ **余额预警**\n\n'
                        f'🏦 源机器人余额不足 ${self.BALANCE_WARNING_THRESHOLD}\n'
                        f'当前余额: ${balance:.2f}\n'
                        '建议充值以确保后续订单顺利处理'
                    )
                
                if balance < required_amount:
                    shortage = required_amount - balance
                    # 向上取整（源机器人只接受整数充值）
                    import math
                    recharge_amount = math.ceil(shortage + 1)  # 补差价 + 1u，向上取整
                    
                    print(f'⚠️ 余额不足！需要: ${required_amount:.2f}, 当前: ${balance:.2f}')
                    print(f'💰 自动充值 ${recharge_amount} (整数)...')
                    
                    try:
                        await self.auto_recharge(recharge_amount)
                        print('✅ 充值成功，继续购买')
                    except Exception as e:
                        error_msg = str(e)
                        
                        # 如果是 OKPay 余额不足，管理员已经收到通知了
                        if 'OKPay 钱包余额不足' in error_msg:
                            raise Exception(f'自动充值失败: {error_msg}')
                        else:
                            # 其他错误，通知管理员
                            await self.notify_admin(
                                '⚠️ **充值失败**\n\n'
                                f'错误信息: {error_msg}\n'
                                f'订单 #{order_id}\n'
                                f'用户: {user_id}'
                            )
                            raise Exception(f'自动充值失败: {error_msg}\n请手动充值后重试')
                else:
                    print(f'✅ 余额充足 (需要: ${required_amount:.2f}, 余额: ${balance:.2f})')
                
                # 记录购买前的最后消息ID（用于隔离）
                msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
                last_msg_id = msgs[0].id if msgs else 0
                print(f'📍 起始消息ID: {last_msg_id}')
                
                # 1. 导航到分类
                await self._navigate_to_category(category)
                
                # 2. 查找并点击商品
                await self._click_product(name)
                
                # 3. 点击购买
                await self._click_buy()
                
                # 4. 输入数量
                await self._input_quantity(quantity)
                
                # 5. 确认购买
                await self._confirm_purchase()
                
                # 6. 等待并接收文件（只接收 last_msg_id 之后的）
                files = await self._wait_for_files(after_msg_id=last_msg_id, save_dir=user_dir)
                
                print(f'✅ 订单 #{order_id} 代购成功: 收到 {len(files)} 个文件')
                return files
                
            except Exception as e:
                print(f'❌ 订单 #{order_id} 代购失败: {e}')
                raise
    
    async def _navigate_to_category(self, category):
        """导航到分类"""
        # 发送 🏠主菜单 回到主页
        await self.client.send_message(Config.SOURCE_BOT, '🏠主菜单')
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
    
    async def _wait_for_files(self, after_msg_id=0, save_dir=None):
        """
        等待并接收文件（txt + 2个zip）
        
        Args:
            after_msg_id: 只接收这个消息ID之后的文件（隔离机制）
            save_dir: 文件保存目录（用户隔离）
        """
        print(f'⏳ 等待文件（仅接收消息ID > {after_msg_id}）...')
        
        if save_dir is None:
            save_dir = Config.ORDER_FILES_DIR
        
        files = []
        start_time = asyncio.get_event_loop().time()
        timeout = 60  # 60秒超时
        
        while len(files) < 3:  # 1 txt + 2 zip = 3个文件
            # 检查超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise Exception('接收文件超时')
            
            # 获取最新消息
            msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=10)
            
            for msg in msgs:
                # 🔒 关键隔离：只接收 after_msg_id 之后的消息
                if msg.id <= after_msg_id:
                    continue
                
                if msg.document and msg.id not in [f['msg_id'] for f in files]:
                    file_ext = (msg.file.ext or '').lower()
                    
                    # 只接收 txt 和 zip 文件，忽略 mp4
                    if file_ext not in ['.txt', '.zip']:
                        print(f'  ⏭ 跳过文件: {msg.file.name} (类型: {file_ext})')
                        continue
                    
                    # 获取文件信息
                    file_name = msg.file.name or f'file_{len(files) + 1}{file_ext}'
                    
                    # 下载文件到用户目录
                    file_path = await msg.download_media(file=save_dir)
                    
                    files.append({
                        'msg_id': msg.id,
                        'path': file_path,
                        'name': file_name,
                        'ext': file_ext,
                        'size': msg.file.size
                    })
                    
                    # 显示文件类型
                    file_type = '📄 TXT' if file_ext == '.txt' else '📦 ZIP'
                    print(f'  ✅ {file_type} 接收 {len(files)}/3: {file_name} ({msg.file.size} bytes)')
                    
                    if len(files) >= 3:
                        break
            
            await asyncio.sleep(2)
        
        return files
    
    async def check_balance(self):
        """查询代购账号余额"""
        # 发送主菜单命令
        await self.client.send_message(Config.SOURCE_BOT, '🏠主菜单')
        await asyncio.sleep(2)
        
        # 获取最新消息
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        
        if msgs and msgs[0]:
            # 使用 message 属性而不是 text（避免 Markdown 格式问题）
            text = msgs[0].message if hasattr(msgs[0], 'message') else msgs[0].text
            
            if not text:
                print('⚠️ 消息为空，返回 0')
                return 0
            
            # 解析余额（格式：🏦 USDT : 2.87 或 💰 USDT: 2.87 或 USDT:2.87）
            import re
            # 尝试多种模式
            patterns = [
                r'USDT\s*[:：]\s*(\d+\.?\d*)',  # 🏦 USDT : 2.87 / USDT: 2.87
                r'余额\s*[:：]\s*(\d+\.?\d*)',  # 余额: 2.87
                r'(\d+\.?\d*)\s*USDT',         # 2.87 USDT
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    balance = float(match.group(1))
                    print(f'💰 代购账号余额: ${balance}')
                    return balance
            
            # 无法解析时，打印调试信息
            print(f'⚠️ 无法解析余额')
            print(f'   原始文本: {repr(text[:200])}')
            
            # 打印十六进制（查找特殊字符）
            for line in text.split('\n'):
                if 'USDT' in line:
                    import binascii
                    print(f'   USDT行: {repr(line)}')
                    print(f'   HEX: {binascii.hexlify(line.encode()).decode()}')
                    break
        
        # 无法获取余额时返回 0
        print('⚠️ 返回余额 0')
        return 0
    
    async def auto_recharge(self, amount):
        """通过源机器人自动充值（OKPay）"""
        # 确保金额是整数
        amount = int(amount)
        print(f'💰 开始自动充值 ${amount}...')
        
        # 1. 返回主菜单
        await self.client.send_message(Config.SOURCE_BOT, '🏠主菜单')
        await asyncio.sleep(2)
        
        # 2. 点击"充值余额"
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        if msgs and msgs[0].buttons:
            clicked = False
            for row in msgs[0].buttons:
                for btn in row:
                    if '充值' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        print('  ✅ 已点击"充值余额"')
                        clicked = True
                        break
                if clicked:
                    break
            
            if not clicked:
                raise Exception('未找到"充值余额"按钮')
        
        # 3. 点击"自定义金额"
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        if msgs and msgs[0].buttons:
            clicked = False
            for row in msgs[0].buttons:
                for btn in row:
                    if '自定义' in btn.text:
                        await btn.click()
                        await asyncio.sleep(2)
                        print('  ✅ 已点击"自定义金额"')
                        clicked = True
                        break
                if clicked:
                    break
            
            if not clicked:
                raise Exception('未找到"自定义金额"按钮')
        
        # 4. 输入金额
        await self.client.send_message(Config.SOURCE_BOT, str(amount))
        await asyncio.sleep(3)
        print(f'  ✅ 已输入金额: {amount}')
        
        # 5. 提取支付链接并打开
        msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=1)
        payment_url = None
        
        if msgs and msgs[0].text and msgs[0].entities:
            from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
            
            for entity in msgs[0].entities:
                if isinstance(entity, MessageEntityTextUrl):
                    # 文本超链接（"点击付款"）
                    payment_url = entity.url
                    print(f'  ✅ 找到支付链接: {payment_url}')
                    break
                elif isinstance(entity, MessageEntityUrl):
                    # 普通 URL
                    offset = entity.offset
                    length = entity.length
                    payment_url = msgs[0].text[offset:offset+length]
                    print(f'  ✅ 找到支付链接: {payment_url}')
                    break
        
        if not payment_url:
            raise Exception('未找到支付链接')
        
        # 6. 打开支付链接（如果是 t.me/okpay 开头）
        # Telethon 会自动处理深链接
        if 'okpay' in payment_url or 't.me' in payment_url:
            print('  ✅ 正在打开 OKPay 支付页面...')
            
            # 提取 start 参数（例如：t.me/okpay?start=xxx）
            import re
            start_match = re.search(r'start=([^&]+)', payment_url)
            if start_match:
                start_param = start_match.group(1)
                # 正确的 Bot 用户名：@okpay（不是 @okpaybot）
                await self.client.send_message('@okpay', f'/start {start_param}')
            else:
                # 没有 start 参数，直接发送链接
                await self.client.send_message('@okpay', '/start')
            
            await asyncio.sleep(3)
        else:
            print(f'  ⚠️ 未知的支付链接格式: {payment_url}')
        
        # 7. 点击"确认支付"（在 OKPay Bot 中）
        msgs = await self.client.get_messages('@okpay', limit=1)
        if msgs and msgs[0].buttons:
            clicked = False
            for row in msgs[0].buttons:
                for btn in row:
                    # 查找"确认支付"按钮
                    if '确认' in btn.text or 'Confirm' in btn.text or '✓' in btn.text or '支付' in btn.text:
                        await btn.click()
                        await asyncio.sleep(3)
                        print('  ✅ 已点击"确认支付"（OKPay）')
                        clicked = True
                        break
                if clicked:
                    break
            
            if not clicked:
                raise Exception('未找到"确认支付"按钮（OKPay）')
        else:
            raise Exception('OKPay Bot 未返回按钮')
        
        # 8. 等待余额更新（监听到账提醒，不刷主菜单）
        print('  ⏳ 等待充值到账（最多 150 秒）...')
        old_balance = await self.check_balance()
        
        # 最多等待 150 秒（2.5 分钟），每 10 秒检查一次消息
        for i in range(15):
            await asyncio.sleep(10)
            
            # 检查是否有到账提醒消息（必须包含"到账提醒"或"账户余额"）
            msgs = await self.client.get_messages(Config.SOURCE_BOT, limit=5)
            for msg in msgs:
                msg_text = msg.message if hasattr(msg, 'message') else (msg.text or '')
                
                # 严格检测到账提醒（必须包含"到账"或"账户余额"）
                if ('到账提醒' in msg_text or '账户余额' in msg_text) and 'USDT' in msg_text:
                    print(f'  ✅ 检测到到账提醒: {msg_text[:80]}...')
                    
                    # 确认余额是否真的增加了
                    new_balance = await self.check_balance()
                    if new_balance > old_balance:
                        print(f'✅ 充值成功！余额: ${old_balance} → ${new_balance}')
                        return True
                    else:
                        print(f'  ⚠️ 余额未增加，继续等待... (当前: ${new_balance})')
                
                # 检测充值失败消息
                if '余额不足' in msg_text or '操作失败' in msg_text:
                    print(f'  ❌ 检测到充值失败: {msg_text[:80]}...')
                    
                    # 通知管理员：OKPay 钱包余额不足
                    await self.notify_admin(
                        '⚠️ **余额预警**\n\n'
                        '💳 OKPay 钱包余额不足\n'
                        f'需要充值金额: ${amount}\n'
                        '操作失败，请及时充值 OKPay 钱包'
                    )
                    
                    raise Exception('充值失败：OKPay 钱包余额不足')
            
            # 打印等待进度
            if i % 3 == 0:
                print(f'  ⏳ 等待中... ({(i+1)*10}秒 / 150秒)')
        
        raise Exception('充值超时（150秒），未检测到到账提醒')
    
    async def stop(self):
        """停止客户端"""
        if self.client:
            await self.client.disconnect()
