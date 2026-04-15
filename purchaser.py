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
    
    def __init__(self, client=None):
        self.db = Database()
        self.client = client  # 接收外部传入的客户端
    
    async def start(self):
        """启动客户端（如果没有传入）"""
        if self.client is None:
            from client_manager import ClientManager
            self.client = await ClientManager.get_client()
        print('✅ 代购模块已准备就绪')
    
    async def purchase(self, product_id, quantity=1, user_id=None, order_id=None, source_bot=None, buyer_session=None):
        """
        购买商品（串行处理，确保订单不混淆）
        
        Args:
            product_id: 商品ID
            quantity: 购买数量
            user_id: 用户ID（用于创建隔离目录）
            order_id: 订单ID（用于目录命名）
            source_bot: 源机器人用户名（如 @hao24bot）
            buyer_session: 代购账号 session 文件路径
        
        Returns:
            list: 文件列表 [{'path': ..., 'name': ...}, ...]
        """
        # 使用传入的来源，如果没有则使用默认配置
        source_bot = source_bot or Config.SOURCE_BOT
        buyer_session = buyer_session or Config.BUYER_SESSION
        
        # 创建临时客户端（使用指定的 session）
        temp_client = TelegramClient(buyer_session, Config.API_ID, Config.API_HASH)
        
        # 🔒 全局锁：同一时间只处理一个订单
        async with AutoPurchaser._purchase_lock:
            print(f'🔒 订单 #{order_id} (用户 {user_id}) 开始处理...')
            print(f'📱 使用来源: {source_bot}')
            print(f'🔑 使用 session: {buyer_session}')
            
            try:
                # 启动临时客户端
                await temp_client.start()
                
                # 🎯 创建对应的购买器
                from purchasers import PurchaserFactory
                purchaser = PurchaserFactory.create(source_bot, temp_client)
                
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
                
                # 创建用户专属目录
                user_dir = os.path.join(Config.ORDER_FILES_DIR, str(user_id), f'order_{order_id}')
                os.makedirs(user_dir, exist_ok=True)
                print(f'📁 文件保存路径: {user_dir}')
                
                # ✅ 检查余额并自动充值
                balance = await purchaser.check_balance()
                required_amount = price * quantity
                
                if balance < required_amount:
                    shortage = required_amount - balance
                    # 向上取整（源机器人只接受整数充值）
                    import math
                    recharge_amount = math.ceil(shortage + 1)  # 补差价 + 1u，向上取整
                    
                    print(f'⚠️ 余额不足！需要: ${required_amount:.2f}, 当前: ${balance:.2f}')
                    print(f'💰 自动充值 ${recharge_amount} (整数)...')
                    
                    try:
                        await purchaser.auto_recharge(recharge_amount)
                        print('✅ 充值成功，继续购买')
                    except Exception as e:
                        raise Exception(f'自动充值失败: {e}')
                else:
                    print(f'✅ 余额充足 (需要: ${required_amount:.2f}, 余额: ${balance:.2f})')
                
                # 记录购买前的最后消息ID（用于隔离）
                msgs = await temp_client.get_messages(source_bot, limit=1)
                last_msg_id = msgs[0].id if msgs else 0
                print(f'📍 起始消息ID: {last_msg_id}')
                
                # 1. 导航到分类
                await purchaser.navigate_to_category(category)
                
                # 2. 查找并点击商品
                await purchaser.click_product(name)
                
                # 3. 点击购买
                await purchaser.click_buy()
                
                # 4. 输入数量
                await purchaser.input_quantity(quantity)
                
                # 5. 确认购买
                await purchaser.confirm_purchase()
                
                # 6. 等待并接收文件（只接收 last_msg_id 之后的）
                files = await purchaser.wait_for_files(after_msg_id=last_msg_id, save_dir=user_dir)
                
                print(f'✅ 订单 #{order_id} 代购成功: 收到 {len(files)} 个文件')
                return files
                
            except Exception as e:
                print(f'❌ 订单 #{order_id} 代购失败: {e}')
                raise
            
            finally:
                # 断开临时客户端
                await temp_client.disconnect()
                print(f'✅ 订单 #{order_id} 处理完成')
