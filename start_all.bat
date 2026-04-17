@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 ShopBot 系统一键启动
echo ============================================================
echo.
echo 💡 将启动3个终端窗口：
echo    1. 账号管理Bot（按需）
echo    2. 刷新器（必须）
echo    3. ShopBot（必须）
echo.
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] 启动账号管理Bot...
start "账号管理Bot" cmd /k "python account_manager_bot.py"
timeout /t 2 /nobreak >nul

echo [2/3] 启动刷新器...
start "刷新器" cmd /k "python scraper_pool_manager.py"
timeout /t 2 /nobreak >nul

echo [3/3] 启动ShopBot...
start "ShopBot" cmd /k "python main.py"

echo.
echo ============================================================
echo ✅ 所有服务已启动！
echo ============================================================
echo.
echo 💡 提示：
echo    - 账号管理Bot: 按需使用，可关闭
echo    - 刷新器 + ShopBot: 必须保持运行
echo.
pause
