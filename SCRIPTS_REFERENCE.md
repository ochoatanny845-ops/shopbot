# ShopBot 主要脚本清单

## 🎯 核心运行脚本（后台启动）

### 1. 账号管理Bot
- **文件**: `account_manager_bot.py`
- **启动**: `start_account_manager.bat` 或 `python account_manager_bot.py`
- **功能**: 添加账号 + 接收告警
- **必须**: 🟢 按需（首次部署时必须，日常可关闭）

### 2. 刷新器
- **文件**: `scraper_pool_manager.py`
- **启动**: `start_scraper.bat` 或 `python scraper_pool_manager.py`
- **功能**: 多账号轮换抓取商品
- **必须**: 🔴 是（必须持续运行）

### 3. ShopBot
- **文件**: `main.py`
- **启动**: `start_shopbot.bat` 或 `python main.py`
- **功能**: 销售机器人 + 代购
- **必须**: 🔴 是（必须持续运行）

---

## 🛠️ 辅助工具脚本（按需使用）

### 初始化工具
- **文件**: `init_accounts.py`
- **用途**: 初始化刷新账号（让账号与源机器人建立对话）
- **使用**: `python init_accounts.py`
- **时机**: 添加账号后运行一次

### 账号管理工具
- **文件**: `upload_accounts.py`
- **用途**: 命令行方式添加账号（旧版，不推荐）
- **使用**: `python upload_accounts.py`

- **文件**: `relogin_account.py`
- **用途**: 重新登录指定账号（修复session损坏）
- **使用**: `python relogin_account.py`

- **文件**: `mark_failed.py`
- **用途**: 手动标记账号为失败状态
- **使用**: `python mark_failed.py`

- **文件**: `remove_account.py`
- **用途**: 删除指定账号
- **使用**: `python remove_account.py`

### 配置工具
- **文件**: `update_interval.py`
- **用途**: 手动更新刷新器轮换间隔
- **使用**: `python update_interval.py`
- **注意**: 新版刷新器已支持自动调整，通常无需手动

---

## 📋 快速启动命令

### 方式1：一键启动（Windows）
```bash
双击 start_all.bat
```
会同时启动3个终端窗口。

### 方式2：分别启动（Windows）
```bash
双击 start_account_manager.bat  # 账号管理Bot（按需）
双击 start_scraper.bat          # 刷新器（必须）
双击 start_shopbot.bat          # ShopBot（必须）
```

### 方式3：命令行启动（跨平台）
```bash
# 终端1（按需）
python account_manager_bot.py

# 终端2（必须）
python scraper_pool_manager.py

# 终端3（必须）
python main.py
```

---

## 🔄 更新和重启流程

```bash
# 1. 停止所有进程（每个终端按 Ctrl+C）

# 2. 拉取最新代码
cd E:\工具\shop\shopbot\shopbot-stable
git reset --hard origin/stable-v1

# 3. 重启服务
双击 start_all.bat
# 或分别启动各个脚本
```

---

## 📂 文件结构

```
shopbot/
├── 核心运行脚本
│   ├── account_manager_bot.py      # 账号管理Bot
│   ├── scraper_pool_manager.py     # 刷新器
│   └── main.py                     # ShopBot
│
├── 启动脚本（Windows）
│   ├── start_all.bat               # 一键启动所有
│   ├── start_account_manager.bat   # 账号管理Bot
│   ├── start_scraper.bat           # 刷新器
│   └── start_shopbot.bat           # ShopBot
│
├── 辅助工具
│   ├── init_accounts.py            # 初始化账号
│   ├── upload_accounts.py          # 命令行添加账号
│   ├── relogin_account.py          # 重新登录账号
│   ├── mark_failed.py              # 标记失败账号
│   ├── remove_account.py           # 删除账号
│   └── update_interval.py          # 更新轮换间隔
│
├── 配置文件
│   ├── .env                        # 环境变量配置
│   ├── config.py                   # 系统配置
│   └── accounts_pool.json          # 账号池（运行时生成）
│
├── 数据库
│   └── shopbot.db                  # SQLite数据库
│
└── 文档
    ├── STARTUP_GUIDE.md            # 启动指南
    ├── SCRAPER_POOL_GUIDE.md       # 刷新器使用文档
    └── ACCOUNT_MANAGER_BOT_GUIDE.md # 账号管理Bot文档
```

---

## 🎯 最小运行要求

**必须运行的脚本：**
1. ✅ `scraper_pool_manager.py`（刷新器）
2. ✅ `main.py`（ShopBot）

**按需运行：**
3. 🟢 `account_manager_bot.py`（添加账号或收告警时）

---

## 💡 提示

- 所有 `.bat` 脚本仅限Windows使用
- Linux/Mac 直接用 `python xxx.py` 启动
- 建议用 `screen`、`tmux` 或 `supervisor` 管理后台进程
- 配置文件修改后需要重启相应服务
