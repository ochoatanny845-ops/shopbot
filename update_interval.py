"""
更新轮换间隔为 120 秒
"""
import json
import os

config_file = 'accounts_pool.json'

if not os.path.exists(config_file):
    print('❌ 配置文件不存在')
    print('💡 请在刷新器运行目录执行此脚本')
    exit(1)

with open(config_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

old_interval = data.get('rotation_interval', 60)
data['rotation_interval'] = 120

with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('='*60)
print('✅ 轮换间隔已更新')
print('='*60)
print(f'旧值: {old_interval} 秒')
print(f'新值: 120 秒')
print('='*60)
print()
print('💡 重启刷新器生效')
print('  python scraper_pool_manager.py')
