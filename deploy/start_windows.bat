@echo off
chcp 65001
echo ========================================
echo    台湾PK10项目 - Windows本地部署
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装，请先安装Node.js 16+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python和Node.js环境检查通过
echo.

:: 安装Python依赖
echo 📦 安装Python依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Python依赖安装失败
    pause
    exit /b 1
)

:: 安装Node.js依赖
echo 📦 安装Node.js依赖...
npm install
if %errorlevel% neq 0 (
    echo ❌ Node.js依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成
echo.

:: 设置数据库
echo 🗄️ 设置数据库...
python deploy/windows_database_setup.py
if %errorlevel% neq 0 (
    echo ❌ 数据库设置失败
    pause
    exit /b 1
)

echo ✅ 数据库设置完成
echo.

:: 启动服务
echo 🚀 启动服务...
echo.
echo 正在启动以下服务:
echo - Web服务器 (端口 8000)
echo - API服务器 (端口 3000)
echo - 数据抓取服务
echo.

:: 创建日志目录
if not exist "logs" mkdir logs

:: 启动Web服务器
start "Web服务器" cmd /k "echo 🌐 Web服务器启动中... && python -m http.server 8000"

:: 等待2秒
timeout /t 2 /nobreak >nul

:: 启动API服务器
start "API服务器" cmd /k "echo 🔌 API服务器启动中... && node server.js"

:: 等待2秒
timeout /t 2 /nobreak >nul

:: 启动数据抓取服务
start "数据抓取" cmd /k "echo 📊 数据抓取服务启动中... && python data_fetcher.py"

echo.
echo 🎉 所有服务启动完成！
echo.
echo 📋 访问地址:
echo - 主页面: http://localhost:8000/TWPK.html
echo - 管理页面: http://localhost:8000/index.html
echo - API接口: http://localhost:3000/api
echo.
echo 💡 提示:
echo - 关闭此窗口不会停止服务
echo - 要停止服务，请关闭对应的命令行窗口
echo - 或运行 stop_windows.bat 脚本
echo.

:: 询问是否打开浏览器
set /p open_browser="是否打开浏览器? (y/n): "
if /i "%open_browser%"=="y" (
    start http://localhost:8000/TWPK.html
)

echo.
echo 按任意键退出...
pause >nul