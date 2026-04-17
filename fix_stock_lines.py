# -*- coding: utf-8 -*-
"""
Replace stock patterns directly by line number
"""

with open('purchaser.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace lines 222-228 with correct patterns
new_lines = [
    '            stock_patterns = [\n',
    "                r'当前库存[：:]\\s*(\\d+)',\n",
    "                r'库存[：:]\\s*(\\d+)',\n",
    "                r'[Ss]tock[：:]\\s*(\\d+)',\n",
    "                r'当前库存(\\d+)',  # No colon or space\n",
    "                r'库存(\\d+)',\n",
    '            ]\n',
]

# Replace
lines = lines[:221] + new_lines + lines[228:]

with open('purchaser.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed stock patterns (lines 222-228)")
