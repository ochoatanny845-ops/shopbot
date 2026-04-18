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
        self.app.add_handler(CommandHandler('apiadd', self.cmd_apiadd))
        self.app.add_handler(CommandHandler('list', self.cmd_list))
        self.app.add_handler(CommandHandler('del', self.cmd_del))
        self.app.add_handler(CommandHandler('cancel', self.cmd_cancel))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """启动命令"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text('❌ 无权限。本Bot仅供管理员使用。')
            return
        
        await update.message.reply_text(
            '👋 欢迎使用账号管理助手！\n\n'
            '📱 功能：\n'
            '/add - 手动添加账号（需要手动输入验证码）\n'
            '/apiadd - 自动添加账号（通过API自动获取验证码）\n'
            '/list - 查看账号池状态\n'
            '/del #2 #3 - 删除指定账号（支持批量）\n'
            '/cancel - 取消当前操作\n\n'
            '💡 提示：\n'
            '- /add 适合少量添加\n'
            '- /apiadd 适合批量添加（支持文本/文件）\n'
            '- /del 删除失败的账号后可重新添加'
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
    
    async def cmd_apiadd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """自动添加账号命令"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        # 设置状态：等待账号信息
        user_states[user_id] = {'step': 'apiadd_waiting'}
        
        await update.message.reply_text(
            '📱 请发送账号信息\n\n'
            '支持格式：\n'
            '1️⃣ 单行文本\n'
            '   手机号 API链接\n\n'
            '2️⃣ 多行文本\n'
            '   手机号 API链接\n'
            '   手机号 API链接\n'
            '   ...\n\n'
            '3️⃣ TXT文件\n'
            '   上传包含账号信息的文本文件\n\n'
            '示例：\n'
            '5542999004826 https://tgapi88880.duckdns.org/verify/xxx\n\n'
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
    
    async def cmd_del(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """删除账号命令"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text('❌ 无权限')
            return
        
        # 解析账号ID列表
        # 格式: /del #2 #3 #5
        args = context.args
        
        if not args:
            await update.message.reply_text(
                '❌ 请指定要删除的账号ID\n\n'
                '格式：/del #2 #3 #5\n'
                '示例：/del #2\n'
                '批量：/del #2 #3'
            )
            return
        
        # 提取账号ID
        account_ids = []
        for arg in args:
            # 去除#号
            id_str = arg.strip('#')
            try:
                account_id = int(id_str)
                account_ids.append(account_id)
            except ValueError:
                await update.message.reply_text(f'❌ 无效的账号ID: {arg}')
                return
        
        if not account_ids:
            await update.message.reply_text('❌ 未找到有效的账号ID')
            return
        
        # 读取账号池
        config_file = 'accounts_pool.json'
        if not os.path.exists(config_file):
            await update.message.reply_text('❌ 账号池不存在')
            return
        
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            accounts = data.get('accounts', [])
        
        # 查找要删除的账号
        to_delete = []
        not_found = []
        
        for account_id in account_ids:
            found = False
            for acc in accounts:
                if acc['id'] == account_id:
                    to_delete.append(acc)
                    found = True
                    break
            if not found:
                not_found.append(account_id)
        
        if not to_delete:
            await update.message.reply_text(f'❌ 未找到账号: {", ".join(f"#{id}" for id in not_found)}')
            return
        
        # 确认删除
        confirm_text = f'⚠️ 确认删除以下账号？\n\n'
        for acc in to_delete:
            confirm_text += f'#{acc["id"]} {acc["phone"]} ({acc["status"]})\n'
        
        if not_found:
            confirm_text += f'\n❌ 未找到: {", ".join(f"#{id}" for id in not_found)}\n'
        
        confirm_text += '\n回复 yes 确认，其他内容取消'
        
        # 保存待删除列表到状态
        user_states[user_id] = {
            'step': 'delete_confirm',
            'accounts_to_delete': to_delete
        }
        
        await update.message.reply_text(confirm_text)
    
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
        elif step == 'apiadd_waiting':
            await self.handle_apiadd_text(update, state, text)
        elif step == 'apiadd_confirm':
            if text.lower() == 'yes':
                accounts = state.get('apiadd_accounts', [])
                await self.process_apiadd_accounts(update, accounts)
            else:
                await update.message.reply_text('❌ 已取消')
                del user_states[user_id]
        elif step == 'delete_confirm':
            if text.lower() == 'yes':
                accounts_to_delete = state.get('accounts_to_delete', [])
                await self.process_delete_accounts(update, accounts_to_delete)
            else:
                await update.message.reply_text('❌ 已取消删除')
                del user_states[user_id]
    
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
        
        # 备份现有配置
        if os.path.exists(config_file):
            import shutil
            from datetime import datetime
            backup_file = f'{config_file}.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            shutil.copy2(config_file, backup_file)
            print(f'✅ 已备份配置到 {backup_file}')
        
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
        
        # 检查是否已存在该ID，避免重复
        existing_ids = {acc['id'] for acc in data['accounts']}
        if account_id in existing_ids:
            print(f'⚠️ 账号ID {account_id} 已存在，跳过保存')
            return None
        
        data['accounts'].append(new_account)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f'✅ 已保存账号 #{account_id}: {phone}')
        return new_account
    
    async def handle_apiadd_text(self, update: Update, state, text):
        """处理API自动添加的文本输入"""
        from auto_login import AutoLoginHelper
        
        helper = AutoLoginHelper()
        accounts = helper.parse_accounts(text)
        
        if not accounts:
            await update.message.reply_text(
                '❌ 未识别到有效账号\n\n'
                '请检查格式：\n'
                '手机号 API链接\n\n'
                '示例：\n'
                '5542999004826 https://tgapi88880.duckdns.org/verify/xxx'
            )
            return
        
        # 单个账号直接添加，多个账号需确认
        if len(accounts) == 1:
            await self.process_apiadd_accounts(update, accounts)
        else:
            await self.confirm_apiadd_batch(update, state, accounts)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理文件上传"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            return
        
        if user_id not in user_states:
            return
        
        state = user_states[user_id]
        step = state.get('step')
        
        if step != 'apiadd_waiting':
            return
        
        # 下载文件
        file = await update.message.document.get_file()
        file_path = f'temp_{user_id}.txt'
        await file.download_to_drive(file_path)
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f'❌ 读取文件失败：{e}')
            return
        
        # 解析账号
        from auto_login import AutoLoginHelper
        helper = AutoLoginHelper()
        accounts = helper.parse_accounts(text)
        
        if not accounts:
            await update.message.reply_text('❌ 文件中未找到有效账号')
            return
        
        await update.message.reply_text(f'✅ 解析成功，找到 {len(accounts)} 个账号')
        
        # 确认批量添加
        await self.confirm_apiadd_batch(update, state, accounts)
    
    async def confirm_apiadd_batch(self, update: Update, state, accounts):
        """确认批量添加"""
        user_id = update.effective_user.id
        
        # 保存账号列表到状态
        state['apiadd_accounts'] = accounts
        state['step'] = 'apiadd_confirm'
        
        text = f'📋 找到 {len(accounts)} 个账号\n\n'
        for i, acc in enumerate(accounts[:5], 1):
            text += f'{i}. +{acc["phone"]}\n'
        
        if len(accounts) > 5:
            text += f'... 还有 {len(accounts) - 5} 个\n'
        
        text += '\n是否确认批量添加？\n'
        text += '回复 yes 确认，其他内容取消'
        
        await update.message.reply_text(text)
    
    async def process_apiadd_accounts(self, update: Update, accounts):
        """处理API自动添加账号"""
        user_id = update.effective_user.id
        
        from auto_login import AutoLoginHelper
        helper = AutoLoginHelper()
        
        total = len(accounts)
        success = 0
        failed = 0
        
        msg = await update.message.reply_text(f'⏳ 开始批量添加 {total} 个账号...')
        
        # 在循环外获取起始ID，避免ID冲突
        config_file = 'accounts_pool.json'
        next_id = 1
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_accounts = data.get('accounts', [])
                if existing_accounts:
                    next_id = max(a['id'] for a in existing_accounts) + 1
        
        for i, acc in enumerate(accounts, 1):
            phone = acc['phone']
            api_url = acc['api_url']
            
            # 使用递增的ID
            session_file = f'sessions/scraper_{next_id}.session'
            
            # 更新进度
            progress_text = (
                f'⏳ 批量添加进度\n\n'
                f'[{i}/{total}] +{phone}\n'
                f'✅ 成功: {success}\n'
                f'❌ 失败: {failed}'
            )
            await msg.edit_text(progress_text)
            
            # 自动登录
            result = await helper.auto_login(phone, api_url, session_file)
            
            if result['success']:
                # 保存账号
                await self.save_account(next_id, session_file, '+' + phone)
                success += 1
                next_id += 1  # 成功后递增ID
                
                # 更新进度
                progress_text = (
                    f'⏳ 批量添加进度\n\n'
                    f'[{i}/{total}] +{phone} ✅\n'
                    f'✅ 成功: {success}\n'
                    f'❌ 失败: {failed}'
                )
                await msg.edit_text(progress_text)
            else:
                failed += 1
                next_id += 1  # 失败也要递增ID，避免冲突
                error = result.get('error', '未知错误')
                
                # 更新进度
                progress_text = (
                    f'⏳ 批量添加进度\n\n'
                    f'[{i}/{total}] +{phone} ❌\n'
                    f'错误: {error}\n\n'
                    f'✅ 成功: {success}\n'
                    f'❌ 失败: {failed}'
                )
                await msg.edit_text(progress_text)
        
        # 最终结果
        final_text = (
            f'━━━━━━━━━━━━━━━━━━━━\n'
            f'✅ 批量添加完成！\n'
            f'━━━━━━━━━━━━━━━━━━━━\n'
            f'成功: {success}/{total}\n'
            f'失败: {failed}/{total}\n\n'
            f'💡 提示：使用 /list 查看账号池\n'
            f'运行 python init_accounts.py 初始化账号'
        )
        await msg.edit_text(final_text)
        
        # 清除状态
        if user_id in user_states:
            del user_states[user_id]
    
    async def process_delete_accounts(self, update: Update, accounts_to_delete):
        """处理账号删除"""
        user_id = update.effective_user.id
        
        config_file = 'accounts_pool.json'
        
        # 读取配置
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            accounts = data.get('accounts', [])
        
        deleted_count = 0
        deleted_sessions = []
        
        # 删除账号
        for acc_to_del in accounts_to_delete:
            # 从列表中移除
            accounts = [acc for acc in accounts if acc['id'] != acc_to_del['id']]
            
            # 删除session文件
            session_file = acc_to_del['session']
            if os.path.exists(session_file):
                os.remove(session_file)
                deleted_sessions.append(session_file)
            
            # 删除.journal文件
            journal_file = session_file + '.journal'
            if os.path.exists(journal_file):
                os.remove(journal_file)
            
            deleted_count += 1
        
        # 保存配置
        data['accounts'] = accounts
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 报告结果
        result_text = (
            f'✅ 删除完成！\n\n'
            f'已删除 {deleted_count} 个账号:\n'
        )
        
        for acc in accounts_to_delete:
            result_text += f'  ✅ #{acc["id"]} {acc["phone"]}\n'
        
        result_text += f'\n💾 已删除 {len(deleted_sessions)} 个session文件\n'
        result_text += f'\n📊 当前账号池:\n'
        result_text += f'  总账号数: {len(accounts)}\n'
        result_text += f'  可用账号: {sum(1 for a in accounts if a["status"] == "active")}'
        
        await update.message.reply_text(result_text)
        
        # 清除状态
        if user_id in user_states:
            del user_states[user_id]
    
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
