@echo off
chcp 65001 >nul
echo ============================================================
echo 🤖 ShopBot 销售机器人启动
echo ============================================================
echo.
echo 💡 功能：
echo    - Telegram销售机器人
echo    - 用户购买处理
echo    - 代购账号购买商品
echo    - 充值、订单、余额管理
echo.
echo 📊 按 Ctrl+C 停止机器人
echo ============================================================
echo.
cd /d "%~dp0"
python main.py
pause
