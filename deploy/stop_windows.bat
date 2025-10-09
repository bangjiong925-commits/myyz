@echo off
chcp 65001
echo ========================================
echo    停止台湾PK10项目服务
echo ========================================
echo.

echo 🛑 正在停止所有服务...

:: 停止Python HTTP服务器 (端口8000)
echo 停止Web服务器...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: 停止Node.js服务器 (端口3000)
echo 停止API服务器...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: 停止Python数据抓取进程
echo 停止数据抓取服务...
taskkill /f /im python.exe /fi "WINDOWTITLE eq 数据抓取*" >nul 2>&1

:: 停止Node.js进程
echo 停止Node.js进程...
taskkill /f /im node.exe >nul 2>&1

echo.
echo ✅ 所有服务已停止
echo.
echo 📋 已停止的服务:
echo - Web服务器 (端口 8000)
echo - API服务器 (端口 3000) 
echo - 数据抓取服务
echo.

timeout /t 3 /nobreak >nul
echo 按任意键退出...
pause >nul