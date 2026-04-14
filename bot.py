"""
销售机器人模块
"""
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import Config
from database import Database

class SalesBot:
    """销售机器人"""
    
    def __init__(self, purchaser):
        self.db = Database()
        self.purchaser = purchaser
        self.app = None
    
    def start_bot(self):
        """启动机器人"""
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # 注册处理器
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        print(f'✅ 销售机器人启动: @{Config.BOT_USERNAME}')
        self.app.run_polling()
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user
        
        # 保存用户
        self._save_user(user)
        
        # 获取余额
        balance = self._get_balance(user.id)
        
        keyboard = [
            [InlineKeyboardButton("📱 Telegram账号", callback_data="categories")],
            [
                InlineKeyboardButton("💰 充值余额", callback_data="recharge"),
                InlineKeyboardButton("📋 我的订单", callback_data="orders")
            ],
            [InlineKeyboardButton("📢 帮助", callback_data="help")]
        ]
        
        await update.message.reply_text(
            f"👋 欢迎使用账号购买系统！\n\n"
            f"📱 用户ID：`{user.id}`\n"
            f"💰 当前余额：**${balance:.2f} USDT**\n\n"
            f"🛍 请选择服务：",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理回调查询"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "categories":
            await self._show_categories(query)
        elif data.startswith("cat_"):
            category = data[4:]
            await self._show_products(query, category)
        elif data.startswith("buy_"):
            product_id = int(data[4:])
            await self._buy_product(query, product_id)
        elif data == "recharge":
            await self._show_recharge(query)
        elif data == "orders":
            await self._show_orders(query)
        elif data == "help":
            await self._show_help(query)
        elif data == "back_main":
            await self._back_to_main(query)
    
    async def _show_categories(self, query):
        """显示分类列表"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT category, SUM(stock) as total_stock
            FROM products
            WHERE is_active = 1 AND stock > 0
            GROUP BY category
            HAVING total_stock > 0
            ORDER BY category
        ''')
        
        categories = c.fetchall()
        conn.close()
        
        if not categories:
            await query.edit_message_text(
                "⚠️ 暂无商品\n\n请稍后再试！",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回", callback_data="back_main")
                ]])
            )
            return
        
        keyboard = []
        for cat, stock in categories:
            keyboard.append([InlineKeyboardButton(
                f"{cat} 【{stock}】",
                callback_data=f"cat_{cat}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="back_main")])
        
        await query.edit_message_text(
            "📱 请选择分类：",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _show_products(self, query, category):
        """显示商品列表"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT id, name, selling_price, stock
            FROM products
            WHERE category = ? AND is_active = 1 AND stock > 0
            ORDER BY selling_price
            LIMIT 50
        ''', (category,))
        
        products = c.fetchall()
        conn.close()
        
        if not products:
            await query.edit_message_text(
                f"⚠️ 分类 {category} 暂无商品",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回", callback_data="categories")
                ]])
            )
            return
        
        keyboard = []
        for pid, name, price, stock in products:
            keyboard.append([InlineKeyboardButton(
                f"{name} 【{stock}】- ${price}",
                callback_data=f"buy_{pid}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="categories")])
        
        await query.edit_message_text(
            f"📱 {category} 商品列表：\n\n"
            f"共 {len(products)} 个商品",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _buy_product(self, query, product_id):
        """购买商品"""
        user_id = query.from_user.id
        
        # 查询商品
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT name, selling_price, stock, original_price
            FROM products
            WHERE id = ? AND is_active = 1
        ''', (product_id,))
        
        product = c.fetchone()
        
        if not product:
            await query.edit_message_text(
                "❌ 商品不存在或已下架",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回", callback_data="categories")
                ]])
            )
            conn.close()
            return
        
        name, selling_price, stock, original_price = product
        
        if stock <= 0:
            await query.edit_message_text(
                f"❌ 商品 {name} 已售罄",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回", callback_data="categories")
                ]])
            )
            conn.close()
            return
        
        # 检查余额
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        balance = user[0] if user else 0
        
        if balance < selling_price:
            await query.edit_message_text(
                f"❌ 余额不足\n\n"
                f"商品价格：${selling_price}\n"
                f"当前余额：${balance:.2f}\n"
                f"需要充值：${selling_price - balance:.2f}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💰 充值", callback_data="recharge")],
                    [InlineKeyboardButton("🔙 返回", callback_data="categories")]
                ])
            )
            conn.close()
            return
        
        # 创建订单
        c.execute('''
            INSERT INTO orders (user_id, product_id, product_name, quantity, unit_price, total_price, status)
            VALUES (?, ?, ?, 1, ?, ?, 'processing')
        ''', (user_id, product_id, name, selling_price, selling_price))
        
        order_id = c.lastrowid
        
        # 扣除余额
        new_balance = balance - selling_price
        c.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
        
        # 记录余额变动
        c.execute('''
            INSERT INTO balance_logs (user_id, amount, type, order_id, note)
            VALUES (?, ?, 'purchase', ?, ?)
        ''', (user_id, -selling_price, order_id, f'购买 {name}'))
        
        conn.commit()
        conn.close()
        
        await query.edit_message_text(
            f"⏳ 订单处理中...\n\n"
            f"商品：{name}\n"
            f"价格：${selling_price}\n"
            f"订单号：{order_id}\n\n"
            f"正在自动代购，请稍候..."
        )
        
        # 调用代购模块
        try:
            files = await self.purchaser.purchase(product_id)
            
            # 更新订单状态
            conn = self.db.get_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE orders 
                SET status = 'completed', files_path = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (files, order_id))
            conn.commit()
            conn.close()
            
            # 发送文件
            await query.message.reply_document(
                document=open(files, 'rb'),
                caption=f"✅ 购买成功！\n\n"
                        f"商品：{name}\n"
                        f"订单号：{order_id}\n\n"
                        f"账号信息已压缩成ZIP文件，请下载查看。"
            )
            
        except Exception as e:
            # 退款
            conn = self.db.get_connection()
            c = conn.cursor()
            c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (selling_price, user_id))
            c.execute('''
                UPDATE orders 
                SET status = 'failed', error_message = ?
                WHERE id = ?
            ''', (str(e), order_id))
            c.execute('''
                INSERT INTO balance_logs (user_id, amount, type, order_id, note)
                VALUES (?, ?, 'refund', ?, ?)
            ''', (user_id, selling_price, order_id, f'退款：{str(e)}'))
            conn.commit()
            conn.close()
            
            await query.message.reply_text(
                f"❌ 购买失败\n\n"
                f"错误：{str(e)}\n\n"
                f"已自动退款 ${selling_price}"
            )
    
    async def _show_recharge(self, query):
        """显示充值说明"""
        await query.edit_message_text(
            "💰 充值说明\n\n"
            "请联系管理员充值：\n"
            f"管理员ID：`{Config.ADMIN_IDS[0]}`\n\n"
            "充值后余额会自动到账。",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 返回", callback_data="back_main")
            ]]),
            parse_mode='Markdown'
        )
    
    async def _show_orders(self, query):
        """显示订单列表"""
        user_id = query.from_user.id
        
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT id, product_name, total_price, status, created_at
            FROM orders
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        orders = c.fetchall()
        conn.close()
        
        if not orders:
            await query.edit_message_text(
                "📋 暂无订单",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回", callback_data="back_main")
                ]])
            )
            return
        
        text = "📋 我的订单\n\n"
        for oid, name, price, status, created in orders:
            status_emoji = {
                'completed': '✅',
                'processing': '⏳',
                'failed': '❌',
                'pending': '⏸'
            }.get(status, '❓')
            
            text += f"{status_emoji} #{oid} - {name}\n"
            text += f"   ${price} | {created[:16]}\n\n"
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 返回", callback_data="back_main")
            ]])
        )
    
    async def _show_help(self, query):
        """显示帮助"""
        await query.edit_message_text(
            "📢 使用说明\n\n"
            "1. 充值余额\n"
            "2. 选择商品\n"
            "3. 确认购买\n"
            "4. 自动代购\n"
            "5. 接收账号文件\n\n"
            "如有问题，请联系管理员。",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 返回", callback_data="back_main")
            ]])
        )
    
    async def _back_to_main(self, query):
        """返回主菜单"""
        user = query.from_user
        balance = self._get_balance(user.id)
        
        keyboard = [
            [InlineKeyboardButton("📱 Telegram账号", callback_data="categories")],
            [
                InlineKeyboardButton("💰 充值余额", callback_data="recharge"),
                InlineKeyboardButton("📋 我的订单", callback_data="orders")
            ],
            [InlineKeyboardButton("📢 帮助", callback_data="help")]
        ]
        
        await query.edit_message_text(
            f"👋 欢迎使用账号购买系统！\n\n"
            f"📱 用户ID：`{user.id}`\n"
            f"💰 当前余额：**${balance:.2f} USDT**\n\n"
            f"🛍 请选择服务：",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    def _save_user(self, user):
        """保存用户"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_activity)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user.id, user.username, user.first_name, user.last_name))
        
        conn.commit()
        conn.close()
    
    def _get_balance(self, user_id):
        """获取用户余额"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        
        return result[0] if result else 0
