"""
智能重建账号池 - 保留现有数据，只添加新发现的session
"""
import os
import json
from datetime import datetime

sessions_dir = 'sessions'
config_file = 'accounts_pool.json'

# 读取现有配置
if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    existing_accounts = {acc['id']: acc for acc in data.get('accounts', [])}
else:
    data = {
        "accounts": [],
        "current_index": 0,
        "rotation_interval": 60
    }
    existing_accounts = {}

print(f"📊 现有账号数: {len(existing_accounts)}")

# 扫描所有 scraper_X.session 文件
found_sessions = []
for file in sorted(os.listdir(sessions_dir)):
    if file.startswith('scraper_') and file.endswith('.session'):
        try:
            num = int(file.replace('scraper_', '').replace('.session', ''))
            found_sessions.append((num, file))
        except ValueError:
            continue

print(f"🔍 发现 session 文件: {len(found_sessions)} 个")

# 合并数据
accounts = []
added = 0
kept = 0

for num, file in found_sessions:
    if num in existing_accounts:
        # 保留现有账号的所有信息
        accounts.append(existing_accounts[num])
        kept += 1
    else:
        # 添加新账号
        accounts.append({
            "id": num,
            "session": f"sessions/{file}",
            "phone": f"+account_{num}",  # 占位符，需要手动填写
            "status": "active",
            "last_used": 0,
            "success_count": 0,
            "fail_count": 0,
            "banned_at": None
        })
        added += 1
        print(f"  ➕ 新增账号 #{num}")

# 按ID排序
accounts.sort(key=lambda x: x['id'])

# 更新配置
data['accounts'] = accounts

# 保存
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ 重建完成！")
print(f"  📌 保留: {kept} 个账号（包含原有手机号和统计）")
print(f"  ➕ 新增: {added} 个账号（手机号为占位符）")
print(f"  📊 总计: {len(accounts)} 个账号")
print(f"📄 已保存到 {config_file}")
