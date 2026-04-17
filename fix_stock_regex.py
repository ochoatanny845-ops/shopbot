# -*- coding: utf-8 -*-
"""
Fix stock detection regex to match "当前库存:1" (no space)
"""

with open('purchaser.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the stock pattern section
old_patterns = '''            # Match stock patterns
            stock_patterns = [
                r'当前库存[：:]\s*(\d+)',
                r'库存[：:]\s*(\d+)',
                r'[Ss]tock[：:]\s*(\d+)',
            ]'''

new_patterns = '''            # Match stock patterns (with or without space)
            stock_patterns = [
                r'当前库存[：:]\s*(\d+)',
                r'库存[：:]\s*(\d+)',
                r'[Ss]tock[：:]\s*(\d+)',
                r'当前库存(\d+)',  # No colon/space
                r'库存(\d+)',
            ]'''

content = content.replace(old_patterns, new_patterns)

with open('purchaser.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed stock detection regex")
