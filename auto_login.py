"""
自动登录模块 - 通过API自动获取验证码和2FA
"""
import asyncio
import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from config import Config

class AutoLoginHelper:
    """自动登录助手"""
    
    def __init__(self):
        self.config = Config()
    
    def parse_account_line(self, line):
        """解析账号行: 手机号 API链接"""
        line = line.strip()
        if not line:
            return None
        
        # 匹配: 手机号 + 空格/制表符 + URL
        match = re.match(r'(\d+)\s+(https?://[^\s]+)', line)
        if match:
            phone = match.group(1)
            api_url = match.group(2)
            return {'phone': phone, 'api_url': api_url}
        
        return None
    
    def parse_accounts(self, text):
        """解析多行账号信息"""
        accounts = []
        for line in text.split('\n'):
            account = self.parse_account_line(line)
            if account:
                accounts.append(account)
        return accounts
    
    def extract_2fa_from_html(self, html):
        """从API网页提取2FA密码"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找包含2FA的div
            # 结构: <div class="label">两步验证 (2FA) 密码</div>
            #      <div class="row"><span class="val">aa99999</span>
            labels = soup.find_all('div', class_='label')
            for label in labels:
                if '2FA' in label.text or '两步验证' in label.text:
                    # 找到下一个 row div
                    row = label.find_next_sibling('div', class_='row')
                    if row:
                        val = row.find('span', class_='val')
                        if val:
                            return val.text.strip()
            
            return None
        except Exception as e:
            print(f'  [WARN] 提取2FA失败: {e}')
            return None
    
    def get_sse_code(self, api_url, timeout=60):
        """通过SSE监听获取验证码"""
        try:
            # 从API URL提取密钥
            # https://tgapi88880.duckdns.org/verify/20d630c6ff02ed8b09f145dc29721618
            api_key = api_url.split('/')[-1]
            base_url = '/'.join(api_url.split('/')[:-2])
            
            # SSE流地址
            sse_url = f"{base_url}/api/stream/{api_key}"
            
            print(f'  📡 连接SSE: {sse_url}')
            
            # 设置超时
            start_time = time.time()
            
            # 使用requests stream模式
            response = requests.get(sse_url, stream=True, timeout=timeout)
            
            for line in response.iter_lines():
                if time.time() - start_time > timeout:
                    print(f'  ⏱️ SSE超时 ({timeout}秒)')
                    return None
                
                if not line:
                    continue
                
                line = line.decode('utf-8')
                
                # SSE格式: data: {...}
                if line.startswith('data:'):
                    data_str = line[5:].strip()
                    try:
                        data = json.loads(data_str)
                        if 'code' in data:
                            code = data['code']
                            print(f'  ✅ 收到验证码: {code}')
                            return code
                    except json.JSONDecodeError:
                        continue
            
            return None
            
        except Exception as e:
            print(f'  ❌ SSE监听失败: {e}')
            return None
    
    async def auto_login(self, phone, api_url, session_name):
        """自动登录账号"""
        print(f'\n📱 开始自动登录: {phone}')
        print(f'📡 API: {api_url}')
        
        # 删除已存在的session文件（避免冲突）
        if os.path.exists(session_name):
            os.remove(session_name)
        if os.path.exists(session_name + '.journal'):
            os.remove(session_name + '.journal')
        
        try:
            # 1. 获取API配置
            print(f'  [1/5] 📡 获取API配置...')
            response = requests.get(api_url, timeout=30)
            html = response.text
            
            # 2. 提取2FA密码
            print(f'  [2/5] 🔑 提取2FA密码...')
            two_fa = self.extract_2fa_from_html(html)
            if two_fa:
                print(f'  ✅ 2FA密码: {two_fa}')
            else:
                print(f'  ⚠️ 未找到2FA密码')
            
            # 3. 创建客户端并发起登录
            print(f'  [3/5] 📱 发起登录请求...')
            client = TelegramClient(
                session_name,
                self.config.API_ID,
                self.config.API_HASH
            )
            
            await client.connect()
            
            # 等待连接稳定
            if not await client.is_user_authorized():
                print(f'  ✅ 连接成功，准备发送验证码')
            
            # 格式化手机号（确保有+号）
            if not phone.startswith('+'):
                phone = '+' + phone
            
            # 发送验证码请求（添加重试机制）
            max_retries = 3
            for retry in range(max_retries):
                try:
                    await client.send_code_request(phone)
                    break
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f'  ⚠️ 发送验证码失败（重试 {retry + 1}/{max_retries}）: {e}')
                        await asyncio.sleep(2)
                    else:
                        raise
            
            # 4. 监听SSE获取验证码
            print(f'  [4/5] ⏳ 等待验证码 (最多60秒)...')
            
            # 在后台运行SSE监听（避免阻塞asyncio）
            loop = asyncio.get_event_loop()
            code = await loop.run_in_executor(None, self.get_sse_code, api_url, 60)
            
            if not code:
                await client.disconnect()
                return {'success': False, 'error': '未收到验证码'}
            
            # 5. 自动登录
            print(f'  [5/5] 🔐 自动登录...')
            
            try:
                # 尝试使用验证码登录
                await client.sign_in(phone, code)
                print(f'  ✅ 登录成功！')
                
            except SessionPasswordNeededError:
                # 需要2FA
                if not two_fa:
                    return {'success': False, 'error': '需要2FA但未找到密码'}
                
                print(f'  🔑 输入2FA密码...')
                await client.sign_in(password=two_fa)
                print(f'  ✅ 2FA验证成功！')
            
            except PhoneCodeInvalidError:
                return {'success': False, 'error': '验证码无效'}
            
            return {
                'success': True,
                'phone': phone,
                'session': session_name,
                'two_fa': two_fa
            }
            
        except Exception as e:
            print(f'  ❌ 登录失败: {e}')
            return {'success': False, 'error': str(e)}
        
        finally:
            # 确保断开连接
            if 'client' in locals() and client.is_connected():
                await client.disconnect()
                print(f'  🔌 连接已关闭')
