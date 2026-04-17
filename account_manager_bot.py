"""
账号管理Bot - 通过Telegram交互式上传刷新账号
Token: 8680801765:AAH9C4uERN9-14hq7p4kfN1EX2wg744syEc
"""
import asyncio
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from config import Config

# Bot Token
ACCOUNT_MANAGER_BOT_TOKEN = '8680801765:AAH9C4uERN9-14hq7p4kfN1EX2wg744syEc'

# 管理员ID（只有管理员可以添加账号）
ADMIN_ID = 5991190607

# 用户状态
user_states = {}

class AccountManagerBot:
    """账号管理Bot"""
    
    def __init__(self):
        self.app = Application.builder().token(ACCOUNT_MANAGER_BOT_TOKEN).concurrent_updates(True).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置处理器"""
        self.app.add_handler(CommandHandler('start', self.cmd_start))
        self.app.add_handler(CommandHandler('add', self.cmd_add))
        self.app.add_handler(CommandHandler('list', self.cmd_list))
        self.app.add_handler(CommandHandler('cancel', self.cmd_cancel))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """启动命令"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text('❌ 无权限。本Bot仅供管理员使用。')
            return
        
        await update.message.reply_text(
            '👋 欢迎使用账号管理助手！\n\n'
            '📱 功能：\n'
            '/add - 添加新的刷新账号\n'
            '/list - 查看账号池状态\n'
            '/cancel - 取消当前操作\n\n'
            '💡 提示：添加账号时需要输入验证码'
        )
    
    async def cmd_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """添加账号命令"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        # 设置状态：等待输入手机号
        user_states[user_id] = {'step': 'phone'}
        
        await update.message.reply_text(
            '📱 请输入手机号\n\n'
            '格式：+8613800138000\n'
            '提示：必须以 + 开头，包含国家代码\n\n'
            '发送 /cancel 取消'
        )
    
    async def cmd_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """查看账号列表"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        # 读取账号池
        config_file = 'accounts_pool.json'
        if not os.path.exists(config_file):
            await update.message.reply_text('📭 账号池为空\n\n使用 /add 添加账号')
            return
        
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            accounts = data.get('accounts', [])
        
        if not accounts:
            await update.message.reply_text('📭 账号池为空')
            return
        
        # 统计
        active = sum(1 for acc in accounts if acc['status'] == 'active')
        banned = sum(1 for acc in accounts if acc['status'] == 'banned')
        failed = sum(1 for acc in accounts if acc['status'] == 'failed')
        
        text = f'📊 账号池状态\n\n'
        text += f'总数：{len(accounts)}\n'
        text += f'✅ 可用：{active}\n'
        text += f'🔴 封禁：{banned}\n'
        text += f'⚠️ 失败：{failed}\n\n'
        text += '─────────────────\n'
        
        for acc in accounts:
            status_emoji = {
                'active': '✅',
                'banned': '🔴',
                'failed': '⚠️'
            }.get(acc['status'], '❓')
            
            text += f'{status_emoji} #{acc["id"]} {acc["phone"]} (成功{acc["success_count"]}次)\n'
        
        await update.message.reply_text(text)
    
    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """取消操作"""
        user_id = update.effective_user.id
        
        if user_id in user_states:
            del user_states[user_id]
            await update.message.reply_text('✅ 已取消')
        else:
            await update.message.reply_text('💡 没有进行中的操作')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理文本消息"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        if user_id != ADMIN_ID:
            return
        
        if user_id not in user_states:
            return
        
        state = user_states[user_id]
        step = state['step']
        
        if step == 'phone':
            await self.handle_phone_input(update, state, text)
        elif step == 'code':
            await self.handle_code_input(update, state, text)
        elif step == 'password':
            await self.handle_password_input(update, state, text)
    
    async def handle_phone_input(self, update: Update, state, phone):
        """处理手机号输入"""
        user_id = update.effective_user.id
        
        if not phone.startswith('+'):
            await update.message.reply_text('❌ 手机号必须以 + 开头\n例如：+8613800138000')
            return
        
        # 获取下一个账号ID
        config_file = 'accounts_pool.json'
        next_id = 1
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                accounts = data.get('accounts', [])
                if accounts:
                    next_id = max(acc['id'] for acc in accounts) + 1
        
        session_file = f'sessions/scraper_{next_id}.session'
        
        await update.message.reply_text(f'📞 正在发送验证码到 {phone}...')
        
        try:
            # 创建Telethon客户端
            client = TelegramClient(session_file, Config.API_ID, Config.API_HASH)
            await client.connect()
            
            # 发送验证码
            result = await client.send_code_request(phone)
            
            # 保存状态
            state['step'] = 'code'
            state['phone'] = phone
            state['session_file'] = session_file
            state['client'] = client
            state['phone_code_hash'] = result.phone_code_hash
            state['account_id'] = next_id
            
            await update.message.reply_text(
                f'✅ 验证码已发送到 {phone}\n\n'
                f'📝 请输入验证码（纯数字）\n'
                f'提示：检查Telegram消息'
            )
            
        except Exception as e:
            await update.message.reply_text(f'❌ 发送验证码失败：{e}')
            del user_states[user_id]
    
    async def handle_code_input(self, update: Update, state, code):
        """处理验证码输入"""
        user_id = update.effective_user.id
        
        client = state['client']
        phone = state['phone']
        phone_code_hash = state['phone_code_hash']
        
        await update.message.reply_text('⏳ 正在验证...')
        
        try:
            # 尝试登录
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            
            # 登录成功
            me = await client.get_me()
            
            await update.message.reply_text(
                f'✅ 登录成功！\n\n'
                f'姓名：{me.first_name}\n'
                f'手机：{me.phone}\n'
                f'ID：{me.id}'
            )
            
            # 保存账号
            await self.save_account(state['account_id'], state['session_file'], me.phone)
            
            await update.message.reply_text(
                f'💾 账号已保存为 #{state["account_id"]}\n\n'
                f'使用 /add 继续添加\n'
                f'使用 /list 查看账号池'
            )
            
            await client.disconnect()
            del user_states[user_id]
            
        except SessionPasswordNeededError:
            # 需要两步验证密码
            state['step'] = 'password'
            await update.message.reply_text(
                '🔐 该账号启用了两步验证\n\n'
                '请输入两步验证密码'
            )
            
        except PhoneCodeInvalidError:
            await update.message.reply_text(
                '❌ 验证码错误\n\n'
                '请重新输入验证码'
            )
            
        except Exception as e:
            await update.message.reply_text(f'❌ 登录失败：{e}')
            await client.disconnect()
            del user_states[user_id]
    
    async def handle_password_input(self, update: Update, state, password):
        """处理两步验证密码"""
        user_id = update.effective_user.id
        
        client = state['client']
        
        await update.message.reply_text('⏳ 正在验证密码...')
        
        try:
            await client.sign_in(password=password)
            
            me = await client.get_me()
            
            await update.message.reply_text(
                f'✅ 登录成功！\n\n'
                f'姓名：{me.first_name}\n'
                f'手机：{me.phone}\n'
                f'ID：{me.id}'
            )
            
            # 保存账号
            await self.save_account(state['account_id'], state['session_file'], me.phone)
            
            await update.message.reply_text(
                f'💾 账号已保存为 #{state["account_id"]}\n\n'
                f'使用 /add 继续添加\n'
                f'使用 /list 查看账号池'
            )
            
            await client.disconnect()
            del user_states[user_id]
            
        except Exception as e:
            await update.message.reply_text(f'❌ 密码错误：{e}')
            await client.disconnect()
            del user_states[user_id]
    
    async def save_account(self, account_id, session_file, phone):
        """保存账号到配置文件"""
        config_file = 'accounts_pool.json'
        
        new_account = {
            'id': account_id,
            'session': session_file,
            'phone': phone,
            'status': 'active',
            'last_used': 0,
            'success_count': 0,
            'fail_count': 0,
            'banned_at': None
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                'accounts': [],
                'current_index': 0,
                'rotation_interval': 60
            }
        
        data['accounts'].append(new_account)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    async def start(self):
        """启动Bot"""
        print('='*60)
        print('🤖 账号管理Bot启动')
        print('='*60)
        print(f'管理员ID: {ADMIN_ID}')
        print('='*60)
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
        # 保持运行
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print('\n⚠️ 正在关闭...')
    
    async def stop(self):
        """停止Bot"""
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

async def main():
    """主函数"""
    bot = AccountManagerBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())
