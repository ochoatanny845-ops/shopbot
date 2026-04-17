@echo off
chcp 65001 >nul
echo ============================================================
echo 🤖 账号管理Bot启动脚本
echo ============================================================
echo.
echo 💡 使用方式：
echo    1. 在Telegram搜索这个Bot
echo    2. 发送 /start 开始
echo    3. 使用 /add 添加账号
echo.
echo ============================================================
cd /d "%~dp0"
python account_manager_bot.py
pause
