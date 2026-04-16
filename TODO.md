# Shopbot 待修复问题清单

## 📋 待修复问题（2026-04-16 18:18 最终版）

### ❌ 问题1：商品名显示"共和国"中文残留
**截图证据：** 有
**问题描述：**
- 订单处理消息中国家名仍显示中文"共和国"
- 翻译逻辑可能有问题

**位置：** bot.py 订单处理消息
**原因：** translate_product_name() 翻译不完整
**修复方案：** 检查并修复翻译逻辑

---

### ❌ 问题2：产品类型按钮显示优化
**截图证据：** 有
**问题描述：**
- 第一：删除"可用数量"文字，直接显示 `TG💎tdata+session+api (394489)`
- 第二：删除"📱📱"重复emoji，换不同的emoji

**位置：** bot.py 商品总览页面按钮
**当前显示：** `TG💎tdata+session+api 可用数量 (394489)`
**期望显示：** `TG💎tdata+session+api (394489)`

---

### ❌ 问题3：余额不足提示未翻译
**截图证据：** 无（用户文字描述）
**问题描述：**
```
❌ 余额不足

总价:$0.57
当前余额:$0.34
需要充值:$0.23
```
全部是中文，需要翻译

**位置：** bot.py _process_quantity 函数
**修复方案：** 添加翻译键并使用 get_text()

---

### ❌ 问题4：OKPay充值崩溃
**错误日志：**
```
AttributeError: 'RechargeHandler' object has no attribute 'okpay'
```

**位置：** recharge_handler.py Line 200
**原因：** RechargeHandler.__init__() 缺少 `self.okpay` 初始化
**修复方案：** 添加 `self.okpay = OKPayHandler()`

---

### ❌ 问题5：TRC20取消充值崩溃
**错误日志：**
```
NameError: name 'lang' is not defined
```

**位置：** bot.py Line 726 `_cancel_recharge` 函数
**原因：** 函数中使用了 `lang` 但未定义
**修复方案：** 在函数开头添加 `lang = self.get_user_language(user_id) or 'zh'`

---

### ❌ 问题6：充值模块完全未翻译
**问题描述：**
- TRC20充值流程界面全中文
- OKPay充值流程界面全中文
- 所有提示消息都是硬编码中文

**位置：** recharge_handler.py
**修复方案：** 
- 添加充值相关翻译键到 language.py
- 所有硬编码中文改用 get_text()

---

### ❌ 问题7：订单处理中商品名未翻译
**问题描述：**
- 商品列表中显示翻译正确（如"Kenya"）
- 但订单处理消息中仍显示中文（如"肯尼亚"）
- 每个国家都有这个问题

**位置：** bot.py Line ~573 订单处理消息
**原因：** `state['product_name']` 存储的是原始中文商品名
**修复方案：** 使用 `translate_product_name(state['product_name'], lang)` 翻译

---

### ❌ 问题8：文件名类型翻译
**用户确认的翻译规则：**
```
直登号 → tdata
协议号 → session
API → api
```

**位置：** bot.py 文件发送时的文件名翻译
**修复方案：** 在 language.py 添加文件类型翻译映射

---

## ✅ 已修复问题（今日完成）
1. ✅ 充值功能崩溃（self.db 未定义）
2. ✅ 管理后台HTML乱码
3. ✅ 国家名翻译重复（"共和国"独立翻译导致重复）
4. ✅ 订单消息Emoji重复
5. ✅ 商品描述翻译（58个映射）
6. ✅ 用户信息显示优化（"用户ID" → "您的ID:"）
7. ✅ 产品类型文案修正（"直登+协议+api" → "tdata+session+api"）
8. ✅ 国家名简称补充（刚果金、波斯尼亚）
9. ✅ 购买流程变量未定义错误（lang, translated_product_name）
10. ✅ 购买流程消息翻译

---

## 🎯 修复优先级
1. **紧急（崩溃）：** 问题4（OKPay崩溃）、问题5（TRC20取消崩溃）
2. **高优先级：** 问题3（余额不足）、问题6（充值模块翻译）、问题7（订单商品名）
3. **中优先级：** 问题1（共和国残留）、问题2（按钮优化）
4. **低优先级：** 问题8（文件名类型）

---

## 📝 笔记
- 用户ID: 5991190607
- 项目路径: E:\工具\shop\shopbot\shopbot-stable
- 工作分支: stable-v1
- 最新commit: 9dddb6e (修复充值崩溃+管理后台乱码)
- 待修复问题总数：8个
