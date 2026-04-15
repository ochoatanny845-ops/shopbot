"""
销售机器人模块
"""
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import Config
from database import Database
from recharge_handler import RechargeHandler

class SalesBot:
    """销售机器人"""
    
    def __init__(self, purchaser):
        self.db = Database()
        self.purchaser = purchaser
        self.app = None
        self.user_states = {}  # 用户状态管理
        self.recharge_handler = RechargeHandler()  # 充值处理器
    
    def build_app(self):
        """构建应用（不启动）"""
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # 注册处理器
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("add", self.cmd_add_balance))
        self.app.add_handler(CommandHandler("recharge", self.cmd_recharge))  # 充值命令
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print(f'✅ 销售机器人已构建: @{Config.BOT_USERNAME}')
        return self.app
    
    async def start(self):
        """启动机器人（异步方式）"""
        if self.app is None:
            self.build_app()
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        print(f'✅ 销售机器人已启动: @{Config.BOT_USERNAME}')
    
    async def stop(self):
        """停止机器人"""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
    
    async def cmd_add_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """管理员余额调整命令"""
        user_id = update.effective_user.id
        
        # 检查权限
        if user_id not in Config.ADMIN_IDS:
            await update.message.reply_text("❌ 无权限")
            return
        
        # 解析参数
        if len(context.args) < 2:
            await update.message.reply_text(
                "📖 使用方法：\n"
                "/add <用户ID> <金额>\n\n"
                "例如：\n"
                "/add 5991190607 10     # 充值 $10\n"
                "/add 5991190607 -5    # 扣款 $5"
            )
            return
        
        try:
            target_user_id = int(context.args[0])
            amount = float(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ 参数格式错误")
            return
        
        # 调整余额
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # 确保用户存在
        c.execute('SELECT balance FROM users WHERE user_id = ?', (target_user_id,))
        user = c.fetchone()
        
        if not user:
            await update.message.reply_text(f"❌ 用户 {target_user_id} 不存在")
            conn.close()
            return
        
        old_balance = user[0]
        new_balance = old_balance + amount
        
        # 检查余额不能为负
        if new_balance < 0:
            await update.message.reply_text(
                f"❌ 余额不足\n\n"
                f"当前余额：${old_balance:.2f}\n"
                f"扣款金额：${abs(amount):.2f}\n"
                f"差额：${abs(new_balance):.2f}"
            )
            conn.close()
            return
        
        # 更新余额
        c.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, target_user_id))
        
        # 记录日志
        log_type = 'recharge' if amount > 0 else 'deduct'
        note = f"管理员{'充值' if amount > 0 else '扣款'}"
        
        c.execute('''
            INSERT INTO balance_logs (user_id, amount, type, note)
            VALUES (?, ?, ?, ?)
        ''', (target_user_id, amount, log_type, note))
        
        conn.commit()
        conn.close()
        
        # 发送确认消息给管理员
        emoji = "✅" if amount > 0 else "⚠️"
        action = "充值" if amount > 0 else "扣款"
        
        await update.message.reply_text(
            f"{emoji} {action}成功\n\n"
            f"用户ID：`{target_user_id}`\n"
            f"金额：${amount:+.2f}\n"
            f"原余额：${old_balance:.2f}\n"
            f"新余额：${new_balance:.2f}",
            parse_mode='Markdown'
        )
        
        # 发送通知给用户
        try:
            if amount > 0:
                # 充值通知
                user_message = (
                    f"💰 充值成功\n\n"
                    f"充值金额：**${amount:.2f}**\n"
                    f"当前余额：**${new_balance:.2f}**\n\n"
                    f"感谢您的充值！现在可以购买账号了 🎉"
                )
            else:
                # 扣款通知
                user_message = (
                    f"⚠️ 余额变动通知\n\n"
                    f"扣款金额：**${abs(amount):.2f}**\n"
                    f"当前余额：**${new_balance:.2f}**\n\n"
                    f"如有疑问，请联系管理员"
                )
            
            await context.bot.send_message(
                chat_id=target_user_id,
                text=user_message,
                parse_mode='Markdown'
            )
            
            print(f"✅ 已发送通知给用户 {target_user_id}")
            
        except Exception as e:
            print(f"⚠️ 发送用户通知失败: {e}")
            # 不影响充值流程，只记录错误
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user
        
        # 保存用户
        self._save_user(user)
        
        # 获取余额
        balance = self._get_balance(user.id)
        
        keyboard = [
            [InlineKeyboardButton("📱 Telegram账号", callback_data="show_product_overview")],
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
    
    async def cmd_recharge(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /recharge 充值命令"""
        await self.recharge_handler.handle_recharge_start(update, context)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理回调查询"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "show_product_overview":
            await self._show_product_overview(query)
        elif data == "show_categories":
            await self._show_categories(query)
        elif data.startswith("cat_"):
            category = data[4:]
            await self._show_products(query, category)
        elif data.startswith("buy_"):
            product_id = int(data[4:])
            await self._buy_product(query, product_id)
        elif data == "recharge":
            await self._show_recharge(query)
        elif data.startswith("recharge_method_"):
            method = data.split('_')[2]  # trc20 or okpay
            await self.recharge_handler.handle_recharge_method_selection(update, context, method)
        elif data.startswith("cancel_recharge_"):
            order_id = int(data.split('_')[2])
            await self._cancel_recharge(query, order_id)
        elif data.startswith("cancel_okpay_"):
            order_id = int(data.split('_')[2])
            await self._cancel_okpay_recharge(query, order_id)
        elif data.startswith("check_okpay_"):
            # 处理 OKPay 订单查询
            await self.recharge_handler.handle_check_okpay(update, context)
        elif data == "orders":
            await self._show_orders(query)
        elif data == "help":
            await self._show_help(query)
        elif data == "main_menu" or data == "back_main":
            await self._back_to_main(query)
    
    async def _show_product_overview(self, query):
        """显示商品总览（中间层）"""
        # 统计总库存
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT SUM(stock) as total_stock
            FROM products
            WHERE is_active = 1 AND stock > 0
        ''')
        
        result = c.fetchone()
        total_stock = result[0] if result and result[0] else 0
        conn.close()
        
        keyboard = [
            [InlineKeyboardButton(
                f"TG💎直登+协议+api 百万库存 ({total_stock}个)",
                callback_data="show_categories"
            )],
            [InlineKeyboardButton("🏠 返回主菜单", callback_data="back_main")]
        ]
        
        await query.edit_message_text(
            "📱 **Telegram账号商品**\n\n"
            "请选择商品类型：",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
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
                    InlineKeyboardButton("🏠 返回主菜单", callback_data="back_main")
                ]])
            )
            return
        
        keyboard = []
        for cat, stock in categories:
            keyboard.append([InlineKeyboardButton(
                f"{cat} 【{stock}】",
                callback_data=f"cat_{cat}"
            )])
        
        keyboard.append([InlineKeyboardButton("⬅️ 返回上级", callback_data="show_product_overview")])
        
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
                    InlineKeyboardButton("⬅️ 返回分类", callback_data="show_categories"),
                    InlineKeyboardButton("🏠 主菜单", callback_data="back_main")
                ]])
            )
            return
        
        keyboard = []
        for pid, name, price, stock in products:
            keyboard.append([InlineKeyboardButton(
                f"{name} 【{stock}】- ${price}",
                callback_data=f"buy_{pid}"
            )])
        
        keyboard.append([
            InlineKeyboardButton("⬅️ 返回分类", callback_data="show_categories"),
            InlineKeyboardButton("🏠 主菜单", callback_data="back_main")
        ])
        
        await query.edit_message_text(
            f"📱 {category} 商品列表：\n\n"
            f"共 {len(products)} 个商品",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _buy_product(self, query, product_id):
        """购买商品 - 提示输入数量"""
        user_id = query.from_user.id
        
        # 查询商品
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT name, selling_price, stock
            FROM products
            WHERE id = ? AND is_active = 1
        ''', (product_id,))
        
        product = c.fetchone()
        conn.close()
        
        if not product:
            await query.edit_message_text(
                "❌ 商品不存在或已下架",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ 返回分类", callback_data="show_categories")
                ]])
            )
            return
        
        name, selling_price, stock = product
        
        if stock <= 0:
            await query.edit_message_text(
                f"❌ 商品 {name} 已售罄",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ 返回分类", callback_data="show_categories")
                ]])
            )
            return
        
        # 设置用户状态：等待输入数量
        self.user_states[user_id] = {
            'action': 'buy_quantity',
            'product_id': product_id,
            'product_name': name,
            'price': selling_price,
            'stock': stock
        }
        
        await query.edit_message_text(
            f"📱 商品信息\n\n"
            f"🛍 商品：{name}\n"
            f"💰 单价：${selling_price} USDT\n"
            f"📦 库存：{stock} 个\n\n"
            f"💬 请输入购买数量（1-{stock}）：",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ 取消", callback_data="show_categories")
            ]])
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理文本消息（购买数量 / 充值金额 / TxID验证）"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        # 优先检查是否是充值流程
        if context.user_data.get('waiting_for') == 'recharge_amount':
            await self.recharge_handler.handle_amount_message(update, context)
            return
        
        # 检查是否是 TxID（64 位十六进制）
        if len(text) == 64 and all(c in '0123456789abcdefABCDEF' for c in text):
            await self.recharge_handler.handle_txid_verification(update, context)
            return
        
        # 检查用户状态（购买数量输入）
        if user_id not in self.user_states:
            return
        
        state = self.user_states[user_id]
        
        if state['action'] == 'buy_quantity':
            await self._process_quantity(update, state, text)
    
    async def _process_quantity(self, update, state, text):
        """处理购买数量输入"""
        user_id = update.effective_user.id
        
        # 验证数量
        try:
            quantity = int(text)
            if quantity <= 0 or quantity > state['stock']:
                await update.message.reply_text(
                    f"❌ 数量无效\n\n"
                    f"请输入 1-{state['stock']} 之间的数字"
                )
                return
        except ValueError:
            await update.message.reply_text(
                "❌ 请输入有效的数字"
            )
            return
        
        # 计算总价
        total_price = state['price'] * quantity
        
        # 检查余额
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        balance = user[0] if user else 0
        
        if balance < total_price:
            await update.message.reply_text(
                f"❌ 余额不足\n\n"
                f"总价：${total_price:.2f}\n"
                f"当前余额：${balance:.2f}\n"
                f"需要充值：${total_price - balance:.2f}"
            )
            conn.close()
            del self.user_states[user_id]
            return
        
        # 创建订单
        c.execute('''
            INSERT INTO orders (user_id, product_id, product_name, quantity, unit_price, total_price, status)
            VALUES (?, ?, ?, ?, ?, ?, 'processing')
        ''', (user_id, state['product_id'], state['product_name'], quantity, state['price'], total_price))
        
        order_id = c.lastrowid
        
        # 扣除余额
        new_balance = balance - total_price
        c.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
        
        # 记录余额变动
        c.execute('''
            INSERT INTO balance_logs (user_id, amount, type, order_id, note)
            VALUES (?, ?, 'purchase', ?, ?)
        ''', (user_id, -total_price, order_id, f'购买 {state["product_name"]} x{quantity}'))
        
        conn.commit()
        conn.close()
        
        # 清除状态
        del self.user_states[user_id]
        
        await update.message.reply_text(
            f"⏳ 订单处理中...\n\n"
            f"🛍 商品：{state['product_name']}\n"
            f"💰 单价：${state['price']}\n"
            f"📦 数量：{quantity}\n"
            f"💵 总价：${total_price:.2f}\n"
            f"📋 订单号：{order_id}\n\n"
            f"正在自动代购，请稍候..."
        )
        
        # 调用代购模块（传递 user_id 和 order_id 用于隔离）
        try:
            files = await self.purchaser.purchase(
                product_id=state['product_id'],
                quantity=quantity,
                user_id=user_id,
                order_id=order_id
            )
            
            # 更新订单状态
            conn = self.db.get_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE orders 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (order_id,))
            conn.commit()
            conn.close()
            
            # 发送购买成功消息
            caption = (
                f"🗂 购买商品: {state['product_name']}\n"
                f"💰 商品价格: {state['price']} USDT\n"
                f"🛍 购买数量: {quantity}\n\n"
                f"🗂文件打包完成 ♻️存活账号{quantity}\n"
            )
            
            await update.message.reply_text(caption)
            
            # 发送 3 个文件
            for file_info in files:
                await update.message.reply_document(
                    document=open(file_info['path'], 'rb'),
                    filename=file_info['name']
                )
            
            # 发送使用说明
            await update.message.reply_text(
                "📄 协议号: 适用于软件或脚本\n"
                "🗂 直登号: 适用于在电脑直接登入\n"
                "📎 Api链接: 适用于在网页上接收验证码以登录其他设备\n\n"
                "✅ 所有账号均已删除缓存\n"
                "⚠️ 请妥善保管好您的文件"
            )
            
        except Exception as e:
            # 退款
            conn = self.db.get_connection()
            c = conn.cursor()
            c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (total_price, user_id))
            c.execute('''
                UPDATE orders 
                SET status = 'failed', error_message = ?
                WHERE id = ?
            ''', (str(e), order_id))
            c.execute('''
                INSERT INTO balance_logs (user_id, amount, type, order_id, note)
                VALUES (?, ?, 'refund', ?, ?)
            ''', (user_id, total_price, order_id, f'退款：{str(e)}'))
            conn.commit()
            conn.close()
            
            await update.message.reply_text(
                f"❌ 购买失败\n\n"
                f"错误：{str(e)}\n\n"
                f"已自动退款 ${total_price:.2f}"
            )
    
    async def _show_recharge(self, query):
        """显示充值方式选择"""
        keyboard = []
        
        # TRC20 充值（始终可用）
        keyboard.append([InlineKeyboardButton("💎 USDT TRC20 充值", callback_data='recharge_method_trc20')])
        
        # OKPay 充值（如果已配置）
        if hasattr(Config, 'OKPAY_SHOP_ID') and Config.OKPAY_SHOP_ID:
            keyboard.append([InlineKeyboardButton("⚡ OKPay 快速充值", callback_data='recharge_method_okpay')])
        
        keyboard.append([InlineKeyboardButton("🏠 返回主菜单", callback_data='back_main')])
        
        try:
            await query.edit_message_text(
                '💰 **选择充值方式**\n\n'
                '💎 **USDT TRC20 充值**\n'
                '   - 去中心化，资金直达\n'
                '   - 到账时间：1-3 分钟\n'
                '   - 需要复制交易哈希验证\n\n'
                + ('⚡ **OKPay 快速充值**\n'
                   '   - 点击支付后，点"我已支付"查询\n'
                   '   - 到账时间：即时（需手动确认）\n'
                   '   - 一键支付，简单快捷\n\n' 
                   if hasattr(Config, 'OKPAY_SHOP_ID') and Config.OKPAY_SHOP_ID else '') +
                f'最低充值：{Config.MIN_RECHARGE_AMOUNT} USDT',
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        except Exception as e:
            # 如果消息没有变化，忽略错误
            if "Message is not modified" not in str(e):
                raise
    
    async def _cancel_recharge(self, query, order_id):
        """取消充值订单"""
        user_id = query.from_user.id
        
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            UPDATE recharge_orders
            SET status = 'cancelled'
            WHERE id = ? AND user_id = ? AND status = 'pending'
        ''', (order_id, user_id))
        
        conn.commit()
        affected = c.rowcount
        conn.close()
        
        if affected > 0:
            await query.edit_message_text(
                f'✅ 已取消充值订单 #{order_id}',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 返回主菜单", callback_data='back_main')
                ]])
            )
        else:
            await query.answer('❌ 订单不存在或已处理', show_alert=True)
    
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
                    InlineKeyboardButton("🏠 返回主菜单", callback_data="back_main")
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
                InlineKeyboardButton("🏠 返回主菜单", callback_data="back_main")
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
                InlineKeyboardButton("🏠 返回主菜单", callback_data="back_main")
            ]])
        )
    
    async def _back_to_main(self, query):
        """返回主菜单"""
        user = query.from_user
        balance = self._get_balance(user.id)
        
        keyboard = [
            [InlineKeyboardButton("📱 Telegram账号", callback_data="show_categories")],
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
        
        # 使用 INSERT OR IGNORE 避免覆盖余额
        c.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, last_activity)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user.id, user.username, user.first_name, user.last_name))
        
        # 如果用户已存在，只更新活跃时间和用户名
        c.execute('''
            UPDATE users 
            SET username = ?, first_name = ?, last_name = ?, last_activity = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user.username, user.first_name, user.last_name, user.id))
        
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

    async def _cancel_okpay_recharge(self, query, order_id):
        """取消 OKPay 充值订单"""
        user_id = query.from_user.id
        
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            UPDATE okpay_orders
            SET status = 'cancelled'
            WHERE id = ? AND user_id = ? AND status = 'pending'
        ''', (order_id, user_id))
        
        conn.commit()
        affected = c.rowcount
        conn.close()
        
        if affected > 0:
            await query.edit_message_text(
                f'✅ 已取消 OKPay 充值订单 #{order_id}',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton('🏠 返回主菜单', callback_data='back_main')
                ]])
            )
        else:
            await query.answer('❌ 订单不存在或已处理', show_alert=True)
