# ShopBot 版本记录

## v2.0-stable-20260417

**提交编号**: `9701b02`  
**标签**: `v2.0-stable-20260417`  
**日期**: 2026-04-17 17:59 GMT+8  
**分支**: `stable-v1`

### 核心功能
1. ✅ 多账号轮换刷新器（支持20个账号）
2. ✅ 自动清理已售商品（每次抓取前标记旧数据为失效）
3. ✅ 自动调整轮换间隔（根据抓取耗时智能调整）
4. ✅ 账号封禁检测 + Telegram告警
5. ✅ 账号管理Bot（交互式添加/查看账号）
6. ✅ WAL模式数据库（并发读写优化）
7. ✅ 购买并发优化（排队机制 + asyncio让步点）
8. ✅ 完整的启动脚本和文档

### 关键修复
- 修复库存数量不准确问题（自动清理已售商品）
- 修复并发购买时其他用户无响应问题
- 修复数据库锁问题（启用WAL模式）

### 恢复此版本
```bash
cd E:\工具\shop\shopbot\shopbot-stable
git fetch --tags
git checkout v2.0-stable-20260417
```

或：
```bash
git reset --hard 9701b02
```

### 文件清单
- **核心脚本**: main.py, bot.py, scraper.py, scraper_pool_manager.py, account_manager_bot.py
- **启动脚本**: start_all.bat, start_scraper.bat, start_shopbot.bat, start_account_manager.bat
- **工具脚本**: init_accounts.py, upload_accounts.py, relogin_account.py, mark_failed.py, remove_account.py
- **文档**: STARTUP_GUIDE.md, SCRIPTS_REFERENCE.md, SCRAPER_POOL_GUIDE.md, ACCOUNT_MANAGER_BOT_GUIDE.md

---

## 历史版本

### v1.0-stable (之前的备份)
**备份文件**: `shopbot-stable-v2-20260417-143234.zip` (桌面)  
**特点**: 单账号刷新 + 基础购买功能
