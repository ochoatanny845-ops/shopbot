# OKPay 充值功能部署指南

## 功能说明

OKPay 充值是一种基于 OKPay 平台的快速充值方式，用户支付后秒到账，无需手动验证。

---

## 部署步骤

### 1. 配置 .env 文件

在服务器的 `.env` 文件中添加 OKPay 配置：

```env
# OKPay 配置
OKPAY_SHOP_ID=31439
OKPAY_SHOP_TOKEN=VdeDkTmGogXqRuylxvCGHKMbcFoLr4wZ
OKPAY_CALLBACK_PORT=8888
OKPAY_BOT_USERNAME=TGaccbbbot
```

---

### 2. 升级数据库

```powershell
cd E:\工具\shop\shopbot
python upgrade_db_okpay.py
```

**输出：**
```
✅ 数据库升级完成：已添加 OKPay 订单表
```

---

### 3. 安装依赖

```powershell
pip install flask
```

**或：**
```powershell
pip install -r requirements_okpay.txt
```

---

### 4. 开放防火墙端口（重要！）

**Windows 防火墙：**
```powershell
netsh advfirewall firewall add rule name="OKPay Callback" dir=in action=allow protocol=TCP localport=8888
```

**云服务器安全组：**
- 如果是阿里云/腾讯云/AWS 等，需要在控制台开放 `8888` 端口
- 入站规则：允许 TCP `8888` 端口

---

### 5. 启动回调服务器

**方法 1：直接启动（前台）**
```powershell
cd E:\工具\shop\shopbot
python okpay_callback_server.py
```

**方法 2：后台启动（推荐）**
```powershell
# 使用 start 命令在新窗口运行
start python okpay_callback_server.py
```

**启动成功后显示：**
```
🚀 OKPay 回调服务器启动
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
端口: 8888
回调地址: http://188.137.245.150:8888/okpay/callback
健康检查: http://188.137.245.150:8888/health
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6. 重启销售机器人

```powershell
# 停止现有机器人（Ctrl+C）
# 重新启动
cd E:\工具\shop\shopbot
python bot.py
```

---

### 7. 在 OKPay Bot 中设置回调地址

1. 打开 [@OkayPayBot](https://t.me/OkayPayBot)
2. 进入商户管理
3. 点击 `🔔 设置回调地址`
4. 输入：
   ```
   http://188.137.245.150:8888/okpay/callback
   ```
5. 保存

---

## 测试

### 1. 测试回调服务器

在浏览器中访问：
```
http://188.137.245.150:8888/health
```

**应该返回：**
```json
{
  "status": "ok",
  "service": "okpay-callback"
}
```

---

### 2. 测试充值功能

1. 在 Telegram 机器人中发送 `/start`
2. 点击 `💰 充值余额`
3. 选择 `⚡ OKPay 快速充值`
4. 输入金额：`1`
5. 点击 `💰 点击支付`
6. 在 OKPay 中完成支付
7. 自动返回机器人，余额应该立即到账

---

## 架构说明

```
用户充值流程：
  用户点击充值
    ↓
  选择 OKPay 快速充值
    ↓
  输入金额
    ↓
  调用 OKPay API 创建支付链接
    ↓
  用户跳转到 OKPay 支付
    ↓
  支付成功 → OKPay 回调：http://188.137.245.150:8888/okpay/callback
    ↓
  回调服务器验证签名 → 更新数据库 → 增加余额
    ↓
  用户余额自动到账（秒到）
```

---

## 文件说明

| 文件 | 作用 |
|------|------|
| `okpay_handler.py` | OKPay API 封装（创建支付链接、查询订单、签名验证） |
| `okpay_callback_server.py` | 回调服务器（接收 OKPay 回调，处理入账） |
| `recharge_handler.py` | 充值处理器（支持 TRC20 和 OKPay 双通道） |
| `upgrade_db_okpay.py` | 数据库升级脚本（添加 okpay_orders 表） |
| `requirements_okpay.txt` | 依赖清单 |

---

## 常见问题

### 1. 回调服务器无法访问？

**检查：**
- 防火墙是否开放 `8888` 端口
- 云服务器安全组是否开放
- 回调服务器是否正在运行

**测试：**
```powershell
# 在 VPS 上
curl http://188.137.245.150:8888/health
```

---

### 2. 支付后不自动到账？

**检查：**
1. 回调服务器日志（查看是否收到回调）
2. 签名验证是否通过
3. OKPay Bot 中的回调地址是否正确

**查看日志：**
回调服务器会打印所有收到的回调数据

---

### 3. 如何关闭 OKPay 充值？

**临时关闭：**
停止回调服务器即可（用户会看到"创建支付链接失败"）

**永久关闭：**
从 `.env` 中删除 `OKPAY_SHOP_ID` 和 `OKPAY_SHOP_TOKEN`，重启机器人

---

## 优势对比

| 充值方式 | 到账时间 | 用户操作 | 依赖 |
|---------|---------|---------|------|
| **TRC20** | 1-3 分钟 | 复制 TxID 验证 | 区块链网络 |
| **OKPay** | 秒到 | 一键支付 | OKPay 平台 |

---

## 安全说明

- ✅ 回调签名验证（防伪造）
- ✅ 订单唯一性检查（防重复）
- ✅ 金额验证
- ✅ 订单状态检查
- ✅ 用户 ID 匹配

---

## 注意事项

1. **回调服务器必须保持运行**，否则无法自动到账
2. **端口 8888 必须公网可访问**
3. **OKPay 回调地址设置正确**
4. **商户 Token 不要泄露**

---

**部署完成后，用户即可使用 OKPay 快速充值！** ⚡
