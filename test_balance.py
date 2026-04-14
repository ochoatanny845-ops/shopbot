import re
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Real text from logs
text = """👋 凌晨好，[kouwu](https://t.me/daigoubot1)
👤 ID: 8057544486

🏦 USDT : 14.97
💵 消费金额 : 2.48
✅ 购买数量 : 7
-------------------------------
补货频道：@WanGuohaopu"""

print("Testing balance parsing...")
print("="*50)

# Test all patterns
patterns = [
    r'USDT\s*[:：]\s*(\d+\.?\d*)',  # Current
    r'余额\s*[:：]\s*(\d+\.?\d*)',
    r'(\d+\.?\d*)\s*USDT',
]

for i, pattern in enumerate(patterns, 1):
    match = re.search(pattern, text)
    if match:
        print(f"Pattern {i} SUCCESS: {match.group(1)}")
    else:
        print(f"Pattern {i} FAILED")
    print(f"  Regex: {pattern}")
    print()
