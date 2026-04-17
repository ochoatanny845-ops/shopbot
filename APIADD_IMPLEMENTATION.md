# /apiadd 命令实现说明

## 📋 已完成的工作

### 1. 创建了自动登录模块
- 文件: `auto_login.py`
- 功能:
  - 解析账号信息（手机号 + API链接）
  - 从API网页提取2FA密码
  - 通过SSE监听获取验证码
  - 自动登录Telegram账号

### 2. 修改了账号管理Bot
- 文件: `account_manager_bot.py`
- 新增:
  - `/apiadd` 命令
  - 文件上传处理器
  - 智能识别文本/文件输入

## 🚀 剩余工作

由于 `account_manager_bot.py` 文件较长且有编码问题，需要手动添加以下函数：

### 在 `save_account` 函数后添加：

```python
async def handle_apiadd_text(self, update: Update, state, text):
    """处理API自动添加的文本输入"""
    from auto_login import AutoLoginHelper
    
    helper = AutoLoginHelper()
    accounts = helper.parse_accounts(text)
    
    if not accounts:
        await update.message.reply_text(
            '❌ 未识别到有效账号\\n\\n'
            '请检查格式：\\n'
            '手机号 API链接\\n\\n'
            '示例：\\n'
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
    # 保存账号列表到状态
    state['apiadd_accounts'] = accounts
    state['step'] = 'apiadd_confirm'
    
    text = f'📋 找到 {len(accounts)} 个账号\\n\\n'
    for i, acc in enumerate(accounts[:5], 1):
        text += f'{i}. +{acc["phone"]}\\n'
    
    if len(accounts) > 5:
        text += f'... 还有 {len(accounts) - 5} 个\\n'
    
    text += '\\n是否确认批量添加？(回复 yes 确认)'
    
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
    
    for i, acc in enumerate(accounts, 1):
        phone = acc['phone']
        api_url = acc['api_url']
        
        # 获取下一个账号ID
        config_file = 'accounts_pool.json'
        next_id = 1
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_accounts = data.get('accounts', [])
                if existing_accounts:
                    next_id = max(a['id'] for a in existing_accounts) + 1
        
        session_file = f'sessions/scraper_{next_id}.session'
        
        # 更新进度
        progress_text = (
            f'⏳ 批量添加进度\\n\\n'
            f'[{i}/{total}] +{phone}\\n'
            f'✅ 成功: {success}\\n'
            f'❌ 失败: {failed}'
        )
        await msg.edit_text(progress_text)
        
        # 自动登录
        result = await helper.auto_login(phone, api_url, session_file)
        
        if result['success']:
            # 保存账号
            await self.save_account(next_id, session_file, '+' + phone)
            success += 1
        else:
            failed += 1
    
    # 最终结果
    final_text = (
        f'━━━━━━━━━━━━━━━━━━━━\\n'
        f'✅ 批量添加完成！\\n'
        f'━━━━━━━━━━━━━━━━━━━━\\n'
        f'成功: {success}/{total}\\n'
        f'失败: {failed}/{total}\\n\\n'
        f'💡 提示：使用 /list 查看账号池'
    )
    await msg.edit_text(final_text)
    
    # 清除状态
    if user_id in user_states:
        del user_states[user_id]
```

### 在 `handle_message` 中添加确认处理：

```python
elif step == 'apiadd_confirm':
    if text.lower() == 'yes':
        accounts = state.get('apiadd_accounts', [])
        await self.process_apiadd_accounts(update, accounts)
    else:
        await update.message.reply_text('❌ 已取消')
        del user_states[user_id]
```

## 📦 安装依赖

```bash
pip install sseclient-py beautifulsoup4
```

## 🧪 测试

1. 安装依赖
2. 手动合并代码
3. 重启账号管理Bot
4. 发送 `/apiadd`
5. 粘贴账号信息或上传文件

## ⚠️ 注意事项

由于账号管理Bot文件较长且有编码问题，建议：
1. 备份当前文件
2. 手动复制上述代码
3. 仔细检查缩进
4. 测试后再使用

或者等我重新生成完整文件。
