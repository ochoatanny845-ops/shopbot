# 余额监控服务

## 功能

独立的后台服务，定期监控：
- **源机器人余额**（默认阈值：20 USDT）
- **OKPay 钱包余额**（默认阈值：20 USDT）

当余额低于阈值时，自动通知管理员。

## 启动

### 方法 1：直接运行
```bash
python balance_monitor.py
```

### 方法 2：使用启动脚本
```bash
python start_balance_monitor.py
```

## 配置

在 `balance_monitor.py` 中修改：

```python
# 余额预警阈值
SOURCE_BOT_THRESHOLD = 20.0  # 源机器人余额阈值（USDT）
OKPAY_THRESHOLD = 20.0       # OKPay 钱包余额阈值（USDT）

# 检查间隔（秒）
CHECK_INTERVAL = 3600  # 每小时检查一次
```

## 通知示例

### 源机器人余额不足
```
⚠️ **源机器人余额预警**

🏦 当前余额: $15.23
⚠️ 预警阈值: $20.00
💰 建议充值: $14.77

请及时充值以确保订单正常处理
```

### OKPay 钱包余额不足
```
⚠️ **OKPay 钱包余额预警**

💳 当前余额: $12.45
⚠️ 预警阈值: $20.00
💰 建议充值: $17.55

请及时充值 OKPay 钱包
```

## 防刷屏机制

同类型预警间隔至少 **6 小时**，避免频繁通知。

## 后台运行（推荐）

### Linux/macOS
```bash
# 使用 nohup
nohup python balance_monitor.py > balance_monitor.log 2>&1 &

# 使用 screen
screen -S balance_monitor
python balance_monitor.py
# 按 Ctrl+A D 离开

# 使用 systemd (推荐生产环境)
# 创建 /etc/systemd/system/shopbot-balance.service
```

### Windows
```powershell
# 使用 pythonw（无窗口运行）
pythonw balance_monitor.py

# 或创建 Windows 服务（需要第三方工具如 NSSM）
```

## 日志示例

```
🔍 余额监控服务启动中...
✅ 余额监控服务已启动
⏱ 检查间隔: 3600秒 (60分钟)
⚠️ 源机器人阈值: $20.0
⚠️ OKPay 阈值: $20.0
==================================================

[2026-04-15 00:30:00] 开始检查余额...
  ✅ 源机器人余额充足: $25.67
  ✅ OKPay 余额充足: $32.45
检查完成
==================================================

[2026-04-15 01:30:00] 开始检查余额...
  ✅ 源机器人余额充足: $18.23
  ❌ 查询 OKPay 余额失败: timeout
检查完成
==================================================
```

## 注意事项

1. **独立运行**：不影响销售机器人主进程
2. **用户无感知**：只通知管理员，不影响用户体验
3. **轻量级**：每小时只发送 2 次消息（查询余额）
4. **容错性**：单次失败不影响下次检查

## 停止服务

按 `Ctrl+C` 或使用进程管理工具：

```bash
# 查找进程
ps aux | grep balance_monitor

# 停止进程
kill <PID>
```
