"""
充值功能模块
处理用户充值请求和验证
"""
import asyncio
import qrcode
import io
import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from trc20_recharge import TRC20Recharge
from okpay_handler import OKPayHandler
from config import Config
from language import get_text

class RechargeHandler:
    """充值处理器"""
    
    def __init__(self):
        # 语言支持
        self._bot_db = None
    
    def _get_user_language(self, user_id):
        """获取用户语言"""
        if self._bot_db is None:
            self._bot_db = Database()
        conn = self._bot_db.get_connection()
        c = conn.cursor()
        c.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result and result[0] else 'zh'
    
    def __original_init__(self):
        self.db = Database()
        # 动态从数据库读取收款地址
        self.api_key = Config.TRONGRID_API_KEY if hasattr(Config, 'TRONGRID_API_KEY') else None
        
        # 初始化 OKPay 处理器
        self.okpay = OKPayHandler() if hasattr(Config, 'OKPAY_SHOP_ID') and Config.OKPAY_SHOP_ID else None
    
    def get_recipient_address(self):
        """动态获取收款地址"""
        return self.db.get_setting('trc20_address', 'TV77o3KfH8DkQNNEsvDLNo765ABcqr3MnM')
    
    async def handle_recharge_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
        lang = self._get_user_language(user_id)
        """处理充值请求 - 选择充值方式"""
        user_id = update.effective_user.id
        
        # 创建充值方式选择按钮
        keyboard = []
        
        # TRC20 充值（始终可用）
        keyboard.append([InlineKeyboardButton("💎 USDT TRC20 充值", callback_data='recharge_method_trc20')])
        
        # OKPay 充值（如果已配置）
        if self.okpay:
            keyboard.append([InlineKeyboardButton("⚡ OKPay 快速充值", callback_data='recharge_method_okpay')])
        
        keyboard.append([InlineKeyboardButton("🔙 返回", callback_data='main_menu')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            '💰 **选择充值方式**\n\n'
            '💎 **USDT TRC20 充值**\n'
            '   - 去中心化，资金直达\n'
            '   - 到账时间：1-3 分钟\n'
            '   - 需要复制交易哈希验证\n\n'
            + ('⚡ **OKPay 快速充值**\n'
               '   - 支付即到账，无需等待\n'
               '   - 到账时间：秒到\n'
               '   - 一键支付，自动确认\n\n' if self.okpay else '') +
            '最低充值：1 USDT',
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_recharge_method_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
        """处理充值方式选择"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['recharge_method'] = method
        context.user_data['waiting_for'] = 'recharge_amount'
        
        # 发送提示并保存消息 ID
        if method == 'trc20':
            prompt_text = (
                '💎 **USDT TRC20 充值**\n\n'
                '⚠️ 最低充值：1 USDT\n'
                '⚠️ 请输入数字，例如：10'
            )
        else:  # okpay
            prompt_text = (
                '⚡ **OKPay 快速充值**\n\n'
                '⚠️ 最低充值：1 USDT\n'
                '⚠️ 请输入数字，例如：10'
            )
        
        amount_prompt = await query.edit_message_text(
            prompt_text,
            parse_mode='Markdown'
        )
        
        # 保存"请输入充值金额"消息 ID
        context.user_data['amount_prompt_message_id'] = amount_prompt.message_id
        # 发送提示并保存消息 ID
        amount_prompt = await query.edit_message_text(
            '💰 **请输入充值金额**\n\n'
            '⚠️ 最低充值：1 USDT\n'
            '⚠️ 请输入数字，例如：10',
            parse_mode='Markdown'
        )
        
        # 保存"请输入充值金额"消息 ID
        context.user_data['amount_prompt_message_id'] = amount_prompt.message_id
    
    async def handle_amount_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理用户输入的金额"""
        user_id = update.effective_user.id
        
        # 检查是否在等待金额输入
        if context.user_data.get('waiting_for') != 'recharge_amount':
            return
        
        try:
            amount = float(update.message.text.strip())
            
            if amount < 1:
                await update.message.reply_text('❌ 最低充值金额为 1 USDT')
                return
            
            # 获取充值方式
            method = context.user_data.get('recharge_method', 'trc20')
            
            if method == 'okpay':
                # OKPay 充值
                await self._handle_okpay_recharge(update, context, amount)
            else:
                # TRC20 充值（现有逻辑）
                await self._handle_trc20_recharge(update, context, amount)
            
        except ValueError:
            await update.message.reply_text('❌ 请输入有效的数字，例如：10')
    
    async def _handle_trc20_recharge(self, update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
        """处理 TRC20 充值"""
        user_id = update.effective_user.id
        
        # 创建充值订单
        order_id = self._create_recharge_order(user_id, amount)
        
        # 生成支付信息并记录消息 ID
        message_ids = await self._send_payment_info(update, amount, order_id)
        
        # 🗑️ 将"请输入充值金额"提示和用户的金额消息也加入删除列表
        amount_prompt_id = context.user_data.get('amount_prompt_message_id')
        if amount_prompt_id:
            message_ids.insert(0, amount_prompt_id)  # 添加到列表开头
        
        message_ids.insert(1, update.message.message_id)  # 添加用户的金额消息
        
        # 保存消息 ID 到 context，用于后续删除
        context.user_data[f'recharge_messages_{order_id}'] = message_ids
        
        # 清除状态和临时数据
        context.user_data['waiting_for'] = None
        context.user_data['recharge_method'] = None
        if 'amount_prompt_message_id' in context.user_data:
            del context.user_data['amount_prompt_message_id']
    
    async def _handle_okpay_recharge(self, update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
        """处理 OKPay 充值"""
        user_id = update.effective_user.id
        
        # 生成唯一订单号
        unique_id = f"SHOP_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # 创建 OKPay 订单（数据库）
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO okpay_orders (user_id, unique_id, amount, coin, status, created_at)
            VALUES (?, ?, ?, 'USDT', 'pending', ?)
        ''', (user_id, unique_id, amount, datetime.now().isoformat()))
        
        order_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # 调用 OKPay API 创建支付链接
        result = self.okpay.create_payment_link(unique_id, amount)
        
        if not result['success']:
            await update.message.reply_text(
                f'❌ 创建支付链接失败\n\n'
                f'{result["message"]}\n\n'
                f'请稍后重试或联系客服'
            )
            return
        
        pay_url = result['pay_url']
        
        # 删除输入提示和用户金额消息
        amount_prompt_id = context.user_data.get('amount_prompt_message_id')
        if amount_prompt_id:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=amount_prompt_id)
            except:
                pass
        
        try:
            await update.message.delete()
        except:
            pass
        
        # 发送支付链接
        from datetime import timedelta
        expire_time = datetime.now() + timedelta(minutes=10)
        
        keyboard = [
            [InlineKeyboardButton("💰 点击支付", url=pay_url)],
            [InlineKeyboardButton("✅ 我已支付", callback_data=f'check_okpay_{order_id}')],
            [InlineKeyboardButton("❌ 取消充值", callback_data=f'cancel_okpay_{order_id}')]
        ]
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f'⚡ **OKPay 充值订单**\n\n'
                 f'订单号：#{order_id}\n'
                 f'充值金额：`{amount}` USDT\n'
                 f'有效期：10 分钟\n'
                 f'过期时间：{expire_time.strftime("%H:%M:%S")}\n\n'
                 f'💡 **操作步骤：**\n'
                 f'1️⃣ 点击"💰 点击支付"按钮\n'
                 f'2️⃣ 在 OKPay 中完成支付\n'
                 f'3️⃣ **返回这里点击"✅ 我已支付"**\n'
                 f'4️⃣ 系统查询订单后自动到账\n\n'
                 f'⚠️ 支付完成后必须点击"我已支付"才能到账',
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # 清除状态
        context.user_data['waiting_for'] = None
        context.user_data['recharge_method'] = None
        if 'amount_prompt_message_id' in context.user_data:
            del context.user_data['amount_prompt_message_id']
    
    def _create_recharge_order(self, user_id: int, amount: float) -> int:
        """创建充值订单"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO recharge_orders (user_id, amount, status, created_at)
            VALUES (?, ?, 'pending', ?)
        ''', (user_id, amount, datetime.now().isoformat()))
        
        order_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return order_id
    
    async def _send_payment_info(self, update: Update, amount: float, order_id: int):
        """发送支付信息，返回消息 ID 列表"""
        message_ids = []  # 记录所有消息 ID，用于后续删除
        
        # 动态获取收款地址
        recipient_address = self.get_recipient_address()
        
        # 生成二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(recipient_address)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存到内存
        bio = io.BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        
        # 计算有效期（当前时间 + 10 分钟）
        from datetime import datetime, timedelta
        now = datetime.now()
        expire_time = now + timedelta(minutes=10)
        
        # 发送支付信息
        message = (
            f'💰 **充值订单 #{order_id}**\n\n'
            f'充值金额：`{amount}` USDT\n'
            f'网络类型：TRC20 (Tron)\n'
            f'收款地址：\n`{recipient_address}`\n\n'
            f'⏰ **订单时间：**\n'
            f'创建时间：{now.strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'过期时间：{expire_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'有效期：**10 分钟**\n\n'
            f'⚠️ **重要提示：**\n'
            f'1️⃣ 请确保使用 **TRC20 网络**\n'
            f'2️⃣ 转账完成后，发送交易哈希（TxID）\n'
            f'3️⃣ 系统将自动验证并入账\n'
            f'4️⃣ 超过 10 分钟订单自动失效\n\n'
            f'📝 交易哈希格式示例：\n'
            f'`7a1b2c3d4e5f...`'
        )
        
        # 发送二维码
        photo_msg = await update.message.reply_photo(
            photo=bio,
            caption=message,
            parse_mode='Markdown'
        )
        message_ids.append(photo_msg.message_id)
        
        # 提示等待 TxID
        tip_msg = await update.message.reply_text(
            '⏳ 请完成转账后，发送交易哈希（TxID）给我\n\n'
            f'💡 在钱包中复制交易哈希即可\n'
            f'⏰ 请在 {expire_time.strftime("%H:%M:%S")} 前提交',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ 取消充值", callback_data=f'cancel_recharge_{order_id}')
            ]])
        )
        message_ids.append(tip_msg.message_id)
        
        return message_ids  # 返回消息 ID 列表
    
    async def handle_txid_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理用户提交的 TxID"""
        user_id = update.effective_user.id
        txid = update.message.text.strip()
        
        # 简单验证格式（64 位十六进制）
        if len(txid) != 64:
            await update.message.reply_text(
                '❌ 交易哈希格式错误\n\n'
                '正确格式：64 位字符\n'
                '示例：7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d...'
            )
            return
        
        # 查询待验证的充值订单
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT id, amount, created_at FROM recharge_orders
            WHERE user_id = ? AND status = 'pending'
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        
        order = c.fetchone()
        
        if not order:
            await update.message.reply_text('❌ 未找到待充值的订单，请先点击"充值"按钮')
            conn.close()
            return
        
        order_id, expected_amount, order_created_at = order
        
        # 🕐 检查订单是否过期（10 分钟有效期）
        from datetime import datetime
        order_time = datetime.fromisoformat(order_created_at)
        current_time = datetime.now()
        time_elapsed = (current_time - order_time).total_seconds()
        
        if time_elapsed > 600:  # 10 分钟 = 600 秒
            # 订单已过期，标记为失效
            c.execute('''
                UPDATE recharge_orders
                SET status = 'expired'
                WHERE id = ?
            ''', (order_id,))
            conn.commit()
            conn.close()
            
            await update.message.reply_text(
                f'⏰ **充值订单已过期**\n\n'
                f'订单创建时间：{order_created_at}\n'
                f'当前时间：{current_time.isoformat()}\n'
                f'已过去：{time_elapsed / 60:.1f} 分钟\n\n'
                f'⚠️ 充值订单有效期：10 分钟\n'
                f'请重新点击"充值余额"发起新订单',
                parse_mode='Markdown'
            )
            return
        
        # 检查 TxID 是否已被使用
        c.execute('SELECT id FROM recharge_orders WHERE txid = ?', (txid,))
        if c.fetchone():
            await update.message.reply_text('❌ 该交易哈希已被使用')
            conn.close()
            return
        
        conn.close()
        
        # 开始验证
        msg = await update.message.reply_text('🔍 正在验证交易，请稍候...')
        
        # 静默重试机制（最多等待 120 秒）
        max_wait_time = 120  # 秒
        retry_interval = 10  # 每 10 秒检查一次
        max_retries = max_wait_time // retry_interval  # 12 次
        
        for attempt in range(max_retries):
            # 动态获取收款地址
            recipient_address = self.get_recipient_address()
            
            # 初始化验证器
            verifier = TRC20Recharge(recipient_address, self.api_key)
            
            # 验证交易
            result = verifier.verify_transaction(txid, expected_amount)
            
            if result['success']:
                # 验证通过，入账
                break
            
            # 如果是"交易不存在"错误，静默等待后重试
            if '交易不存在' in result.get('message', '') or '尚未上链' in result.get('message', ''):
                if attempt < max_retries - 1:
                    # 静默等待，不提示用户
                    import asyncio
                    await asyncio.sleep(retry_interval)
                else:
                    # 120 秒后仍失败，提示用户
                    await msg.edit_text(
                        f'⏳ **交易验证超时**\n\n'
                        f'已等待 {max_wait_time} 秒，交易仍未上链\n\n'
                        f'💡 **可能的原因：**\n'
                        f'1️⃣ 网络拥堵，交易确认较慢\n'
                        f'2️⃣ 交易哈希复制错误\n'
                        f'3️⃣ 使用了错误的网络（非 TRC20）\n\n'
                        f'🔍 **请检查：**\n'
                        f'在浏览器中确认交易状态：\n'
                        f'https://tronscan.org/#/transaction/{txid}\n\n'
                        f'如交易已确认，请稍后重新发送此 TxID',
                        parse_mode='Markdown'
                    )
                    return
            else:
                # 其他错误，直接返回
                break
        
        if result['success']:
            # ✅ 验证通过，但还需要检查交易时间
            actual_amount = result['amount']
            tx_timestamp = result.get('timestamp', 0)
            
            # 将订单创建时间转为时间戳
            from datetime import datetime
            order_time = datetime.fromisoformat(order_created_at).timestamp()
            
            # 计算时间差（秒）
            time_diff = tx_timestamp - order_time
            
            # 🛡️ 安全检查：交易必须在订单创建后 10 分钟内
            # 允许负值（订单创建前几分钟的交易也可接受，考虑时钟偏差）
            if time_diff < -600:  # 订单创建前 10 分钟
                await msg.edit_text(
                    f'❌ **安全验证失败**\n\n'
                    f'此交易发生在充值订单创建之前！\n\n'
                    f'订单创建时间：{order_created_at}\n'
                    f'交易时间：{datetime.fromtimestamp(tx_timestamp).isoformat()}\n'
                    f'时间差：{abs(time_diff) / 60:.1f} 分钟\n\n'
                    f'⚠️ 不允许使用历史交易充值\n'
                    f'请使用新的转账交易',
                    parse_mode='Markdown'
                )
                return
            
            if time_diff > 600:  # 订单创建后 10 分钟（改为 10 分钟）
                await msg.edit_text(
                    f'⏰ **订单已超时**\n\n'
                    f'订单创建时间：{order_created_at}\n'
                    f'交易时间：{datetime.fromtimestamp(tx_timestamp).isoformat()}\n'
                    f'时间差：{time_diff / 60:.1f} 分钟\n\n'
                    f'⚠️ 充值订单有效期：10 分钟\n'
                    f'请重新发起充值',
                    parse_mode='Markdown'
                )
                return
            
            # 更新订单状态
            conn = self.db.get_connection()
            c = conn.cursor()
            
            c.execute('''
                UPDATE recharge_orders
                SET status = 'completed', txid = ?, actual_amount = ?, completed_at = ?
                WHERE id = ?
            ''', (txid, actual_amount, datetime.now().isoformat(), order_id))
            
            # 增加用户余额
            c.execute('''
                UPDATE users
                SET balance = balance + ?
                WHERE user_id = ?
            ''', (actual_amount, user_id))
            
            conn.commit()
            conn.close()
            
            # 🗑️ 删除充值流程中的临时消息
            try:
                # 获取保存的消息 ID
                saved_messages = context.user_data.get(f'recharge_messages_{order_id}', [])
                
                # 删除订单信息和提示消息
                for message_id in saved_messages:
                    try:
                        await context.bot.delete_message(
                            chat_id=user_id,
                            message_id=message_id
                        )
                    except Exception as e:
                        print(f'  ⚠️ 删除消息失败: {e}')
                
                # 删除用户发送的 TxID 消息
                try:
                    await update.message.delete()
                except Exception as e:
                    print(f'  ⚠️ 删除 TxID 消息失败: {e}')
                
                # 删除"正在验证"消息
                try:
                    await msg.delete()
                except Exception as e:
                    print(f'  ⚠️ 删除验证消息失败: {e}')
                
                # 清除保存的消息 ID
                if f'recharge_messages_{order_id}' in context.user_data:
                    del context.user_data[f'recharge_messages_{order_id}']
                
            except Exception as e:
                print(f'  ⚠️ 清理消息时出错: {e}')
            
            # 发送充值成功通知（新消息）
            await context.bot.send_message(
                chat_id=user_id,
                text=f'✅ **充值成功！**\n\n'
                     f'订单号：#{order_id}\n'
                     f'充值金额：{actual_amount} USDT\n'
                     f'交易哈希：`{txid[:16]}...{txid[-16:]}`\n'
                     f'到账时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                     f'当前余额：${self._get_user_balance(user_id):.2f}',
                parse_mode='Markdown'
            )
        else:
            # 验证失败
            await msg.edit_text(
                f'❌ **验证失败**\n\n'
                f'{result["message"]}\n\n'
                f'如有疑问，请联系客服',
                parse_mode='Markdown'
            )
    
    def _get_user_balance(self, user_id: int) -> float:
        """获取用户余额"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        
        return result[0] if result else 0.0
    
    async def handle_check_okpay(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 OKPay 订单查询（用户点击"我已支付"）"""
        query = update.callback_query
        await query.answer()
        
        # 提取订单号
        order_id = int(query.data.split('_')[2])
        user_id = query.from_user.id
        
        print(f'\n📋 用户查询 OKPay 订单')
        print(f'  订单号: {order_id}')
        print(f'  用户: {user_id}')
        
        # 查询数据库中的订单
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT unique_id, amount, status
            FROM okpay_orders
            WHERE id = ? AND user_id = ?
        ''', (order_id, user_id))
        
        order = c.fetchone()
        conn.close()
        
        if not order:
            await query.edit_message_text('❌ 订单不存在')
            return
        
        unique_id, amount, status = order
        
        # 如果已完成，直接提示
        if status == 'completed':
            await query.edit_message_text(
                f'✅ 该订单已完成！\n\n'
                f'订单号：#{order_id}\n'
                f'充值金额：{amount} USDT\n\n'
                f'当前余额：${self._get_user_balance(user_id):.2f}',
                parse_mode='Markdown'
            )
            return
        
        # 查询 OKPay 订单状态
        await query.edit_message_text('🔍 正在查询订单状态...')
        
        result = self.okpay.check_deposit(unique_id)
        
        print(f'  查询结果: {result}')
        
        if result['success'] and result['status'] == 1:
            # 已支付！更新订单和余额
            conn = self.db.get_connection()
            c = conn.cursor()
            
            # 更新订单状态
            c.execute('''
                UPDATE okpay_orders
                SET status = 'completed',
                    okpay_order_id = ?,
                    actual_amount = ?,
                    completed_at = ?
                WHERE id = ?
            ''', (result['order_id'], result['amount'], datetime.now().isoformat(), order_id))
            
            # 增加用户余额
            c.execute('''
                UPDATE users
                SET balance = balance + ?
                WHERE user_id = ?
            ''', (result['amount'], user_id))
            
            # 记录余额日志
            c.execute('''
                INSERT INTO balance_logs (user_id, amount, type, note)
                VALUES (?, ?, 'recharge', 'OKPay充值')
            ''', (user_id, result['amount']))
            
            conn.commit()
            
            # 获取新余额
            c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            new_balance = c.fetchone()[0]
            
            conn.close()
            
            print(f'  ✅ 充值成功！新余额: {new_balance}')
            
            # 通知用户
            await query.edit_message_text(
                f'✅ **充值成功！**\n\n'
                f'订单号：#{order_id}\n'
                f'充值金额：{result["amount"]} USDT\n'
                f'到账时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                f'当前余额：${new_balance:.2f}',
                parse_mode='Markdown'
            )
        elif result['success'] and result['status'] == 0:
            # 未支付
            await query.edit_message_text(
                f'⏳ **订单未支付**\n\n'
                f'订单号：#{order_id}\n'
                f'充值金额：{amount} USDT\n\n'
                f'请先完成支付，然后再点击"我已支付"',
                reply_markup=query.message.reply_markup  # 保留原按钮
            )
        else:
            # 查询失败
            await query.edit_message_text(
                f'❌ **查询失败**\n\n'
                f'{result.get("message", "未知错误")}\n\n'
                f'请稍后重试或联系客服',
                reply_markup=query.message.reply_markup
            )
