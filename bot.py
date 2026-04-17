"""
销售机器人模块
"""
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import Config
from database import Database
from recharge_handler import RechargeHandler
from admin_handler import AdminHandler
from language import get_text, translate_product_name, translate_category_name
from datetime import datetime, timezone, timedelta

# UTC+8 时区（北京/香港时间）
UTC8 = timezone(timedelta(hours=8))

def get_utc8_now():
    """获取当前UTC+8时间"""
    return datetime.now(UTC8)

def utc_to_utc8(dt):
    """转换UTC时间为UTC+8"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(UTC8)

class SalesBot:
    """销售机器人"""

    def __init__(self, purchaser):
        self.db = Database()
        self.purchaser = purchaser
        self.app = None
        self.user_states = {}  # 用户状态管理
        self.recharge_handler = RechargeHandler()  # 充值处理器
        self.admin_handler = AdminHandler()  # 管理员处理器

    def get_user_language(self, user_id):
        """获取用户语言"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def set_user_language(self, user_id, language):
        """设置用户语言"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
        conn.commit()
        conn.close()

    def build_app(self):
        """构建应用(不启动)"""
        self.app = (
            Application.builder()
            .token(Config.BOT_TOKEN)
            .concurrent_updates(True)  # Enable concurrent updates
            .build()
        )

        # 注册处理器
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("add", self.cmd_add_balance))
        self.app.add_handler(CommandHandler("recharge", self.cmd_recharge))  # 充值命令
        self.app.add_handler(CommandHandler("admin", self.admin_handler.cmd_admin))  # 管理员后台
        self.app.add_handler(CommandHandler("cha", self.admin_handler.cmd_cha))  # 查询用户
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        print(f'✅ 销售机器人已构建: @{Config.BOT_USERNAME}')
        return self.app

    async def start(self):
        """启动机器人(异步方式)"""
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
                "📖 使用方法:\n"
                "/add <用户ID> <金额>\n\n"
                "例如:\n"
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
                f"当前余额:${old_balance:.2f}\n"
                f"扣款金额:${abs(amount):.2f}\n"
                f"差额:${abs(new_balance):.2f}"
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
            f"用户ID:`{target_user_id}`\n"
            f"金额:${amount:+.2f}\n"
            f"原余额:${old_balance:.2f}\n"
            f"新余额:${new_balance:.2f}",
            parse_mode='Markdown'
        )

        # 发送通知给用户
        try:
            if amount > 0:
                # 充值通知
                user_message = (
                    f"💰 充值成功\n\n"
                    f"充值金额:**${amount:.2f}**\n"
                    f"当前余额:**${new_balance:.2f}**\n\n"
                    f"感谢您的充值!现在可以购买账号了 🎉"
                )
            else:
                # 扣款通知
                user_message = (
                    f"⚠️ 余额变动通知\n\n"
                    f"扣款金额:**${abs(amount):.2f}**\n"
                    f"当前余额:**${new_balance:.2f}**\n\n"
                    f"如有疑问,请联系管理员"
                )

            await context.bot.send_message(
                chat_id=target_user_id,
                text=user_message,
                parse_mode='Markdown'
            )

            print(f"✅ 已发送通知给用户 {target_user_id}")

        except Exception as e:
            print(f"⚠️ 发送用户通知失败: {e}")
            # 不影响充值流程,只记录错误

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user

        # 保存用户
        self._save_user(user)

        # 检查用户语言
        user_lang = self.get_user_language(user.id)

        if user_lang is None:
            # 首次使用,显示语言选择
            await self.show_language_selection(update)
            return

        # 已选择语言,显示主菜单
        await self.show_main_menu(update, user.id, user_lang)
    async def cmd_recharge(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /recharge 充值命令"""
        await self.recharge_handler.handle_recharge_start(update, context)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理回调查询"""
        query = update.callback_query
        await query.answer()

        data = query.data
        user_id = query.from_user.id

        # 语言选择回调
        if data.startswith('lang_'):
            lang = data.split('_')[1]
            self.set_user_language(user_id, lang)
            await self.show_main_menu(query, user_id, lang)
            return

        # 切换语言回调
        if data == 'change_language':
            user_lang = self.get_user_language(user_id) or 'zh'
            keyboard = [
                [InlineKeyboardButton('🇺🇸 English', callback_data='lang_en')],
                [InlineKeyboardButton('🇨🇳 中文简体', callback_data='lang_zh')],
                [InlineKeyboardButton(get_text('btn_back', user_lang), callback_data='back_main')]
            ]
            await query.edit_message_text(
                get_text('select_language', user_lang),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # 管理员回调
        if data.startswith('admin_'):
            await self.admin_handler.handle_admin_callback(update, context)
            return

        # 群发回调
        if data.startswith('broadcast_'):
            await self.admin_handler.handle_broadcast_callback(update, context)
            return

        # 自定义按钮类型选择回调
        if data.startswith('btn_type_'):
            await self.admin_handler.handle_admin_callback(update, context)
            return

        # 自定义按钮回调
        if data.startswith('custom_btn_'):
            await self._handle_custom_button(query)
            return

        if data == "show_categories":
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
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'
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
                f"💎 TG {get_text('product_types', lang)} ({total_stock})",
                callback_data="show_categories"
            )],
            [InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_main")]
        ]

        await query.edit_message_text(
            f"🛒 {get_text('btn_products', lang)}\n\n"
            f"{get_text('select_product_type', lang)}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def _show_categories(self, query):
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'
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
                "⚠️ 暂无商品\n\n请稍后再试!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_main")
                ]])
            )
            return

        keyboard = []
        for cat, stock in categories:
            translated_cat = translate_category_name(cat, lang)
            keyboard.append([InlineKeyboardButton(
                f"{translated_cat} 【{stock}】",
                callback_data=f"cat_{cat}"
            )])

        keyboard.append([InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_main")])

        await query.edit_message_text(
            get_text('select_category', lang),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _show_products(self, query, category):
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'
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
                    InlineKeyboardButton(get_text('btn_back_category', lang), callback_data="show_categories"),
                    InlineKeyboardButton(get_text('btn_main_menu', lang), callback_data="back_main")
                ]])
            )
            return

        keyboard = []
        for pid, name, price, stock in products:
            # 翻译商品名
            translated_name = translate_product_name(name, lang)
            keyboard.append([InlineKeyboardButton(
                f"{translated_name} [{stock}] - ${price}",
                callback_data=f"buy_{pid}"
            )])

        keyboard.append([
            InlineKeyboardButton(get_text('btn_back_category', lang), callback_data="show_categories"),
            InlineKeyboardButton(get_text('btn_main_menu', lang), callback_data="back_main")
        ])

        await query.edit_message_text(
            f"{translate_category_name(category, lang)} {get_text('product_list_title', lang)}\n\n"
            f"{get_text('total_products', lang)}: {len(products)} {get_text('pieces', lang)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _buy_product(self, query, product_id):
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'
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
                    InlineKeyboardButton(get_text('btn_back_category', lang), callback_data="show_categories")
                ]])
            )
            return

        name, selling_price, stock = product

        if stock <= 0:
            await query.edit_message_text(
                f"❌ 商品 {name} 已售罄",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text('btn_back_category', lang), callback_data="show_categories")
                ]])
            )
            return

        # 设置用户状态:等待输入数量
        self.user_states[user_id] = {
            'action': 'buy_quantity',
            'product_id': product_id,
            'product_name': name,
            'price': selling_price,
            'stock': stock
        }

        await query.edit_message_text(
            f"📱 {get_text('product_info', lang)}\n\n"
            f"{get_text('product_label', lang)}: {translate_product_name(name, lang)}\n"
            f"{get_text('unit_price_label', lang)}: ${selling_price} USDT\n"
            f"{get_text('stock_label', lang)}: {stock} {get_text('pieces', lang)}\n\n"
            f"{get_text('enter_quantity_prompt', lang)} (1-{stock}):",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text('btn_cancel', lang), callback_data="show_categories")
            ]])
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        lang = self.get_user_language(user_id) or 'zh'
        user_id = update.effective_user.id
        text = update.message.text.strip()

        # 优先处理管理员输入
        admin_waiting = context.user_data.get('admin_waiting_for')
        if admin_waiting:
            if admin_waiting in ['trc20_address', 'start_message', 'notification_url', 'customer_service_url', 'custom_button_text', 'custom_button_message', 'custom_button_url']:
                handled = await self.admin_handler.handle_admin_message(update, context)
                if handled:
                    return
            elif admin_waiting == 'broadcast_message':
                await self.admin_handler.handle_broadcast_message(update, context)
                return
            elif admin_waiting == 'broadcast_button':
                await self.admin_handler.handle_broadcast_button(update, context)
                return

        # 优先检查是否是充值流程
        if context.user_data.get('waiting_for') == 'recharge_amount':
            await self.recharge_handler.handle_amount_message(update, context)
            return

        # 检查是否是 TxID(64 位十六进制)
        if len(text) == 64 and all(c in '0123456789abcdefABCDEF' for c in text):
            await self.recharge_handler.handle_txid_verification(update, context)
            return

        # 检查用户状态(购买数量输入)
        if user_id not in self.user_states:
            return

        state = self.user_states[user_id]

        if state['action'] == 'buy_quantity':
            await self._process_quantity(update, state, text)

    async def _process_quantity(self, update, state, text):
        """处理购买数量输入"""
        user_id = update.effective_user.id
        lang = self.get_user_language(user_id) or 'zh'

        # 验证数量
        try:
            quantity = int(text)
            if quantity <= 0 or quantity > state['stock']:
                await update.message.reply_text(
                    f"{get_text('invalid_quantity', lang)}\n\n"
                    f"{get_text('enter_between', lang)} 1-{state['stock']}"
                )
                return
        except ValueError:
            await update.message.reply_text(
                get_text('invalid_number', lang)
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
                f"❌ {get_text('insufficient_balance', lang)}\n\n"
                f"{get_text('total_price_label', lang)} ${total_price:.2f}\n"
                f"{get_text('current_balance', lang)} ${balance:.2f}\n"
                f"{get_text('need_recharge', lang)} ${total_price - balance:.2f}"
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

        # 翻译商品名
        from language import translate_product_name
        translated_product_name_display = translate_product_name(state['product_name'], lang)
        
        processing_msg = await update.message.reply_text(
            f"{get_text('processing_order', lang)}\n\n"
            f"{get_text('product_label', lang)} {translated_product_name_display}\n"
            f"{get_text('unit_price_label', lang)} ${state['price']}\n"
            f"{get_text('quantity_label', lang)} {quantity}\n"
            f"{get_text('total_price_label', lang)} ${total_price:.2f}\n"
            f"{get_text('order_number_label', lang)} {order_id}\n\n"
            "正在打包账号检查中...\n请稍候，最多2分钟"
        )

        # 检查是否有人正在购买（排队提示）
        queue_message = None
        if self.purchaser._purchase_lock.locked():
            queue_msg = (
                "⏳ 订单已收到！\n\n"
                "前方有订单正在处理中\n"
                "您的订单排在队列中\n\n"
                "预计等待时间：30-90秒\n"
                "请耐心等待..."
            )
            queue_message = await update.message.reply_text(queue_msg)
        
        # 调用代购模块(传递 user_id 和 order_id 用于隔离)
        try:
            result = await self.purchaser.purchase(
                product_id=state['product_id'],
                quantity=quantity,
                user_id=user_id,
                order_id=order_id
            )
            
            # Handle result (dict or list for backward compatibility)
            if isinstance(result, dict):
                files = result['files']
                requested_qty = result['requested_quantity']
                actual_qty = result['actual_quantity']
            else:
                files = result
                requested_qty = quantity
                actual_qty = quantity
            
            # Partial success: refund difference
            if actual_qty < requested_qty:
                refund_qty = requested_qty - actual_qty
                refund_amount = product_price * refund_qty
                
                conn = self.db.get_connection()
                c = conn.cursor()
                c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (refund_amount, user_id))
                c.execute("INSERT INTO balance_logs (user_id, amount, type, order_id, notes) VALUES (?, ?, 'refund', ?, ?)",
                          (user_id, refund_amount, order_id, f'Partial refund: {refund_qty} items'))
                conn.commit()
                conn.close()
                
                print(f'[INFO] Partial success: refunded {refund_amount:.2f} USDT for {refund_qty} items')

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

            # 删除"订单处理中..."的消息
            try:
                await processing_msg.delete()
            except:
                pass  # 如果删除失败,忽略错误
            
            # 删除"排队中..."的消息
            if queue_message:
                try:
                    await queue_message.delete()
                except:
                    pass

            # 翻译商品名
            from language import translate_product_name
            translated_product_name = translate_product_name(state['product_name'], lang)

            # 发送购买成功消息
            caption = (
                f"{get_text('purchase_product', lang)}: {translated_product_name}\n"
                f"{get_text('product_price', lang)}: {state['price']} USDT\n"
                f"{get_text('purchase_quantity', lang)}: {quantity}\n\n"
                f"{get_text('files_packaged', lang)} {quantity}\n"
            )

            await update.message.reply_text(caption)

            # 发送 3 个文件
            for file_info in files:
                # 翻译文件名
                translated_filename = translate_product_name(file_info['name'], lang)
                
                await update.message.reply_document(
                    document=open(file_info['path'], 'rb'),
                    filename=translated_filename
                )

            # 发送使用说明
            await update.message.reply_text(
                f"{get_text('protocol_note', lang)}\n"
                f"{get_text('direct_login_note', lang)}\n"
                f"{get_text('api_link_note', lang)}\n\n"
                f"{get_text('cache_cleared', lang)}\n"
                f"{get_text('keep_files_safe', lang)}"
            )

        except Exception as e:
            # 删除"订单处理中..."的消息
            try:
                await processing_msg.delete()
            except:
                pass
            
            # 删除"排队中..."的消息
            if queue_message:
                try:
                    await queue_message.delete()
                except:
                    pass

            # ❌ 不再自动退款，只标记订单失败
            conn = self.db.get_connection()
            c = conn.cursor()
            # 不再执行: c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', ...)
            c.execute('''
                UPDATE orders
                SET status = 'failed', error_message = ?
                WHERE id = ?
            ''', (str(e), order_id))
            # 不再记录退款日志
            # c.execute('''INSERT INTO balance_logs ... 'refund' ...''')
            conn.commit()
            conn.close()

            # 提示联系客服，不自动退款
            await update.message.reply_text(
                f"{get_text('purchase_failed', lang)}\n\n"
                f"{get_text('error_occurred', lang)}: {str(e)}\n\n"
                f"❌ 订单失败，请联系客服处理\n"
                f"💰 订单金额: ${total_price:.2f}\n"
                f"📝 订单号: #{order_id}"
            )

    async def _show_recharge(self, query):
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'
        """显示充值方式选择"""
        keyboard = []

        # TRC20 充值(始终可用)
        keyboard.append([InlineKeyboardButton(get_text('trc20_recharge', lang), callback_data='recharge_method_trc20')])

        # OKPay 充值(如果已配置)
        if hasattr(Config, 'OKPAY_SHOP_ID') and Config.OKPAY_SHOP_ID:
            keyboard.append([InlineKeyboardButton(get_text('okpay_recharge', lang), callback_data='recharge_method_okpay')])

        keyboard.append([InlineKeyboardButton(get_text('btn_back', lang), callback_data='back_main')])

        text = (
            f"{get_text('select_recharge_method_title', lang)}\n\n"
            f"{get_text('trc20_method_title', lang)}\n"
            f"   - {get_text('trc20_method_desc_1', lang)}\n"
            f"   - {get_text('trc20_method_desc_2', lang)}\n"
            f"   - {get_text('trc20_method_desc_3', lang)}\n\n"
        )
        
        if hasattr(Config, 'OKPAY_SHOP_ID') and Config.OKPAY_SHOP_ID:
            text += (
                f"{get_text('okpay_method_title', lang)}\n"
                f"   - {get_text('okpay_method_desc_1', lang)}\n"
                f"   - {get_text('okpay_method_desc_2', lang)}\n"
                f"   - {get_text('okpay_method_desc_3', lang)}\n\n"
            )
        
        text += get_text('minimum_recharge_notice', lang)

        try:
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        except Exception as e:
            # 如果消息没有变化,忽略错误
            if "Message is not modified" not in str(e):
                raise

    async def _cancel_recharge(self, query, order_id):
        """取消充值订单"""
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'

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
                f'✅ {get_text("recharge_cancelled", lang)} #{order_id}',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text('btn_back', lang), callback_data='back_main')
                ]])
            )
        else:
            await query.answer(f'❌ {get_text("order_not_found_or_processed", lang)}', show_alert=True)

    async def _show_orders(self, query):
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'

        conn = self.db.get_connection()
        c = conn.cursor()

        c.execute('''
            SELECT id, product_name, quantity, unit_price, total_price, status, created_at
            FROM orders
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))

        orders = c.fetchall()
        conn.close()

        if not orders:
            await query.edit_message_text(
                get_text('no_orders', lang),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_main")
                ]])
            )
            return

        text = f"{get_text('my_orders_title', lang)}\n\n"
        for oid, name, qty, unit_price, total_price, status, created in orders:
            status_emoji = {
                'completed': '✅',
                'processing': '⏳',
                'failed': '❌',
                'pending': '⏸'
            }.get(status, '❓')
            
            # 翻译商品名
            translated_name = translate_product_name(name, lang)
            
            # 转换时间为UTC+8（北京时间）
            try:
                # 假设数据库中的时间是UTC或本地时间
                if 'T' in created:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
                    dt = dt.replace(tzinfo=timezone.utc)
                
                # 转换为UTC+8
                dt_utc8 = utc_to_utc8(dt)
                time_str = dt_utc8.strftime('%Y-%m-%d %H:%M')
            except:
                # 如果转换失败，使用原始时间前16个字符
                time_str = created[:16]

            text += f"{status_emoji} #{oid} - {translated_name}\n"
            text += f"   {qty}x ${unit_price} = ${total_price} | {time_str}\n\n"

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_main")
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
            "如有问题,请联系管理员。",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_main")
            ]])
        )

    async def _back_to_main(self, query):
        """返回主菜单"""
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'
        await self.show_main_menu(query, user_id, lang)
    def _save_user(self, user):
        """保存用户"""
        conn = self.db.get_connection()
        c = conn.cursor()

        # 使用 INSERT OR IGNORE 避免覆盖余额
        c.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, last_activity)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user.id, user.username, user.first_name, user.last_name))

        # 如果用户已存在,只更新活跃时间和用户名
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

    async def _handle_custom_button(self, query):
        """处理自定义按钮点击"""
        button_id = int(query.data.split('_')[2])
        user_id = query.from_user.id
        lang = self.get_user_language(user_id) or 'zh'

        # 查询按钮信息
        conn = self.db.get_connection()
        c = conn.cursor()

        c.execute('''
            SELECT text, type, content
            FROM custom_buttons
            WHERE id = ? AND is_active = 1
        ''', (button_id,))

        result = c.fetchone()
        conn.close()

        if not result:
            await query.answer('❌ 按钮不存在', show_alert=True)
            return

        text, btn_type, content = result

        # 消息类型按钮,回复内容
        if btn_type == 'message':
            await query.answer()
            
            # 翻译售后规则内容
            if '售后规则' in text and lang == 'en':
                content = """🔥 First-time buyers are advised to test with a small quantity to avoid unnecessary misunderstandings!
⚠️ Purchase Notice: All accounts are checked for validity before delivery. Dead accounts are automatically refunded!
‼️ In case of account freeze, the delivery time shall prevail!
‼️ Please contact customer service within 30 minutes, otherwise after-sales support will be forfeited!"""
            
            await query.edit_message_text(
                content,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text('btn_back', lang), callback_data='back_main')
                ]]),
                parse_mode='Markdown'
            )
        else:
            # URL 类型(不应该走到这里,因为 URL 按钮直接跳转)
            await query.answer('❌ 按钮类型错误', show_alert=True)


    async def show_language_selection(self, update):
        """显示语言选择菜单"""
        keyboard = [
            [InlineKeyboardButton('🇺🇸 English', callback_data='lang_en')],
            [InlineKeyboardButton('🇨🇳 中文简体', callback_data='lang_zh')]
        ]

        await update.message.reply_text(
            get_text('select_language', 'zh'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_main_menu(self, update_or_query, user_id, lang):
        """显示主菜单(原版简洁布局)"""
        balance = self._get_balance(user_id)
        customer_service_url = self.db.get_setting('customer_service_url', 'https://t.me/id2uu')
        order_notification_url = self.db.get_setting('order_notification_url', 'https://t.me/your_channel')
        
        # 查询用户统计数据
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # 消费金额（已完成订单的总金额）
        c.execute('''
            SELECT COALESCE(SUM(total_price), 0)
            FROM orders
            WHERE user_id = ? AND status = 'completed'
        ''', (user_id,))
        total_spent = c.fetchone()[0]
        
        # 购买数量（已完成订单的总数量）
        c.execute('''
            SELECT COALESCE(SUM(quantity), 0)
            FROM orders
            WHERE user_id = ? AND status = 'completed'
        ''', (user_id,))
        total_orders = c.fetchone()[0]
        
        conn.close()
        
        # 根据语言获取欢迎词
        if lang == 'zh':
            start_message = self.db.get_setting('start_message', get_text('welcome_message', 'zh'))
        else:
            start_message = self.db.get_setting('start_message_en', get_text('welcome_message', 'en'))

        # 原版布局:4个按钮 + 自定义按钮(语言切换移到最底部)
        # Get total stock count
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('SELECT SUM(stock) FROM products WHERE is_active = 1')
        total_stock = c.fetchone()[0] or 0
        conn.close()
        
        keyboard = [
            [InlineKeyboardButton(f'TG✈️ Tdata｜session｜api ({total_stock})', callback_data='show_categories')],
            [
                InlineKeyboardButton(get_text('btn_recharge', lang), callback_data='recharge'),
                InlineKeyboardButton(get_text('btn_orders', lang), callback_data='orders')
            ]
        ]

        # 自定义按钮
        custom_buttons = self.db.get_custom_buttons()
        for btn in custom_buttons:
            # 翻译按钮文字
            btn_text = btn['text']
            if '售后规则' in btn_text and lang == 'en':
                btn_text = '⚠️ After-Sales Rules'
            
            if btn['type'] == 'url':
                keyboard.append([InlineKeyboardButton(btn_text, url=btn['content'])])
            else:
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"custom_btn_{btn['id']}")])

        # 语言切换按钮放在最底部
        keyboard.append([InlineKeyboardButton(get_text('btn_language', lang), callback_data='change_language')])

        # 新格式：欢迎词 + 用户统计 + 链接（使用HTML格式避免Markdown解析问题）
        # 转义HTML特殊字符
        safe_start_message = start_message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        safe_notification_url = order_notification_url.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        safe_customer_url = customer_service_url.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        text = (
            f"{safe_start_message}\n\n"
            f"{get_text('user_stats_id', lang)} <code>{user_id}</code>\n\n"
            f"{get_text('user_stats_balance', lang)} <code>${balance:.2f}</code>\n"
            f"{get_text('user_stats_spent', lang)} <code>${total_spent:.2f}</code>\n"
            f"{get_text('user_stats_orders', lang)} <code>{total_orders}</code>\n"
            f"-------------------------------\n"
            f"{get_text('order_notification', lang)} {safe_notification_url}\n"
            f"{get_text('customer_service', lang)} {safe_customer_url}"
        )

        if hasattr(update_or_query, 'edit_message_text'):
            await update_or_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        else:
            await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
