"""
充值功能模块
处理用户充值请求和验证
"""
import asyncio
import qrcode
import io
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from trc20_recharge import TRC20Recharge
from config import Config

class RechargeHandler:
    """充值处理器"""
    
    def __init__(self):
        self.db = Database()
        # 从 Config 中读取收款地址和 API Key
        self.recipient_address = Config.USDT_RECEIVER_ADDRESS if hasattr(Config, 'USDT_RECEIVER_ADDRESS') else 'TV77o3KfH8DkQNNEsvDLNo765ABcqr3MnM'
        self.api_key = Config.TRONGRID_API_KEY if hasattr(Config, 'TRONGRID_API_KEY') else None
        
        # 初始化验证器（传递 API Key）
        self.verifier = TRC20Recharge(self.recipient_address, self.api_key)
    
    async def handle_recharge_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理充值请求"""
        user_id = update.effective_user.id
        
        # 创建充值订单（待输入金额）
        keyboard = [
            [InlineKeyboardButton("💰 输入充值金额", callback_data='recharge_input_amount')],
            [InlineKeyboardButton("🔙 返回", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            '💰 **USDT 充值**\n\n'
            '支持：USDT TRC20\n'
            '到账时间：1-3 分钟\n'
            '最低充值：1 USDT\n\n'
            '请点击下方按钮输入充值金额',
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理金额输入"""
        query = update.callback_query
        await query.answer()
        
        # 设置用户状态：等待输入金额
        context.user_data['waiting_for'] = 'recharge_amount'
        
        await query.edit_message_text(
            '💰 **请输入充值金额**\n\n'
            '⚠️ 最低充值：1 USDT\n'
            '⚠️ 请输入数字，例如：10',
            parse_mode='Markdown'
        )
    
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
            
            # 创建充值订单
            order_id = self._create_recharge_order(user_id, amount)
            
            # 生成支付信息
            await self._send_payment_info(update, amount, order_id)
            
            # 清除状态
            context.user_data['waiting_for'] = None
            
        except ValueError:
            await update.message.reply_text('❌ 请输入有效的数字，例如：10')
    
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
        """发送支付信息"""
        # 生成二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(self.recipient_address)
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
            f'收款地址：\n`{self.recipient_address}`\n\n'
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
        await update.message.reply_photo(
            photo=bio,
            caption=message,
            parse_mode='Markdown'
        )
        
        # 提示等待 TxID
        await update.message.reply_text(
            '⏳ 请完成转账后，发送交易哈希（TxID）给我\n\n'
            f'💡 在钱包中复制交易哈希即可\n'
            f'⏰ 请在 {expire_time.strftime("%H:%M:%S")} 前提交',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ 取消充值", callback_data=f'cancel_recharge_{order_id}')
            ]])
        )
    
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
        
        # 自动重试机制（等待交易上链）
        max_retries = 3
        retry_delay = 5  # 秒
        
        for attempt in range(max_retries):
            # 验证交易
            result = self.verifier.verify_transaction(txid, expected_amount)
            
            if result['success']:
                # 验证通过，入账
                break
            
            # 如果是"交易不存在"错误，等待后重试
            if '交易不存在' in result.get('message', '') or '尚未上链' in result.get('message', ''):
                if attempt < max_retries - 1:
                    await msg.edit_text(
                        f'⏳ 交易正在上链中...\n\n'
                        f'已尝试 {attempt + 1}/{max_retries} 次\n'
                        f'等待 {retry_delay} 秒后重试...\n\n'
                        f'💡 Tron 网络通常需要 3-10 秒确认'
                    )
                    import asyncio
                    await asyncio.sleep(retry_delay)
                else:
                    # 最后一次失败，给出提示
                    await msg.edit_text(
                        f'⏳ **交易尚未上链**\n\n'
                        f'已尝试 {max_retries} 次验证\n\n'
                        f'💡 **请稍后再试：**\n'
                        f'1️⃣ 等待 10-30 秒\n'
                        f'2️⃣ 重新发送此交易哈希\n'
                        f'3️⃣ 在浏览器中确认交易状态：\n'
                        f'https://tronscan.org/#/transaction/{txid}\n\n'
                        f'交易哈希：`{txid}`',
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
            
            # 通知用户
            await msg.edit_text(
                f'✅ **充值成功！**\n\n'
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
