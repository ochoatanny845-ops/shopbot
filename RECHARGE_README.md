# USDT TRC20 充值功能

## 功能特性

✅ **完全自动验证**
- 验证真实 USDT（防止假币）
- 验证真实转账（防止授权欺诈）
- 验证接收地址
- 验证金额
- 防止重复提交

✅ **用户体验好**
- 自动生成二维码
- 1-3 分钟到账
- 实时验证反馈

✅ **安全可靠**
- 通过 TronGrid API 验证
- 检查合约地址（防假币）
- 检查交易方法（防授权）
- 交易哈希唯一性检查

---

## 配置步骤

### 1. 设置收款地址

在 `.env` 文件中添加：

```env
# USDT TRC20 收款地址
USDT_RECEIVER_ADDRESS=TYourActualAddressHere

# 最低充值金额
MIN_RECHARGE_AMOUNT=1.0
```

### 2. 升级数据库

```bash
python upgrade_db_recharge.py
```

### 3. 集成到 bot.py

在 `bot.py` 中添加充值处理器：

```python
from recharge_handler import RechargeHandler

# 初始化
recharge_handler = RechargeHandler()

# 注册处理器
application.add_handler(CommandHandler('recharge', recharge_handler.handle_recharge_start))
application.add_handler(CallbackQueryHandler(recharge_handler.handle_amount_input, pattern='^recharge_input_amount$'))

# 处理用户输入的金额和 TxID
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recharge_handler.handle_txid_verification))
```

---

## 用户使用流程

### 1. 用户发起充值

```
用户：/recharge
机器人：💰 USDT 充值
       支持：USDT TRC20
       到账时间：1-3 分钟
       最低充值：1 USDT
       
       请点击下方按钮输入充值金额
       [💰 输入充值金额]
```

### 2. 输入金额

```
用户：10
机器人：💰 充值订单 #123
       
       充值金额：10 USDT
       网络类型：TRC20 (Tron)
       收款地址：TYourAddress...
       
       [二维码图片]
       
       ⚠️ 重要提示：
       1️⃣ 请确保使用 TRC20 网络
       2️⃣ 转账完成后，发送交易哈希（TxID）
       3️⃣ 系统将自动验证并入账
```

### 3. 用户转账并提交 TxID

```
用户：7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
机器人：🔍 正在验证交易，请稍候...
```

### 4. 验证结果

**成功：**
```
✅ 充值成功！

订单号：#123
充值金额：10 USDT
交易哈希：7a1b2c3d4e5f...
到账时间：2026-04-15 11:30:00

当前余额：$110.00
```

**失败：**
```
❌ 验证失败

❌ 检测到假币！
合约地址不匹配
期望: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
实际: TXxxxxxx...

如有疑问，请联系客服
```

---

## 验证机制

### 1. 合约地址验证

```python
# USDT 官方合约地址
USDT_CONTRACT = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'

# 拒绝假币
if contract_address != USDT_CONTRACT:
    return False
```

### 2. 交易方法验证

```python
# 必须是 transfer 方法（不是 approve）
if method != 'transfer':
    return False  # 防止授权欺诈
```

### 3. 金额验证

```python
# 允许 1% 误差（手续费）
if actual_amount < expected_amount * 0.99:
    return False
```

### 4. 重复提交检查

```python
# 每个 TxID 只能使用一次
if txid_already_used:
    return False
```

---

## 常见问题

### Q: 支持哪些网络？

**A:** 只支持 **TRC20** 网络（Tron）。

不支持：
- ❌ ERC20 (以太坊)
- ❌ BEP20 (币安智能链)
- ❌ Omni (比特币)

### Q: 如何获取交易哈希？

**A:** 在钱包中查看转账记录：
1. 打开转账详情
2. 复制"交易哈希" / "TxID" / "Transaction Hash"
3. 发送给机器人

### Q: 为什么验证失败？

常见原因：
1. ❌ 使用了错误的网络（ERC20/BEP20）
2. ❌ 转账到错误的地址
3. ❌ 金额不足
4. ❌ 交易尚未确认
5. ❌ 提交了授权交易（而非转账）

### Q: 多久到账？

**A:** 
- Tron 区块确认时间：~3 秒
- 系统验证时间：~5-10 秒
- **总计：1-3 分钟**

### Q: 可以充值其他代币吗？

**A:** 不可以。只支持 **USDT TRC20**。

---

## 安全提示

### 对于用户：
1. ✅ 检查收款地址（防止钓鱼）
2. ✅ 使用正确的网络（TRC20）
3. ✅ 保存交易哈希截图
4. ✅ 不要重复提交同一笔交易

### 对于管理员：
1. ✅ 保护好收款地址私钥
2. ✅ 定期检查充值记录
3. ✅ 监控异常交易
4. ✅ 备份数据库

---

## API 依赖

### TronGrid API

**官网：** https://www.trongrid.io

**API 端点：**
- 查询交易：`GET https://api.trongrid.io/v1/transactions/{txid}`
- 免费使用
- 无需 API Key

**速率限制：**
- 免费：5000 次/天
- Pro：无限制

---

## 数据库表结构

```sql
CREATE TABLE recharge_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,             -- 期望金额
    actual_amount REAL,               -- 实际金额
    txid TEXT UNIQUE,                 -- 交易哈希
    status TEXT DEFAULT 'pending',    -- pending/completed/failed
    created_at TEXT NOT NULL,
    completed_at TEXT
);
```

---

## 未来扩展

可能的功能扩展：
1. 支持 ERC20/BEP20 网络
2. 集成第三方支付网关
3. 自动汇率转换
4. 充值优惠活动
5. VIP 充值通道

---

## 技术支持

如有问题，请查看：
- `trc20_recharge.py` - 核心验证逻辑
- `recharge_handler.py` - 处理器
- `upgrade_db_recharge.py` - 数据库升级脚本
