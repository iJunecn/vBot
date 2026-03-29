@echo off
chcp 65001 >nul
echo ======================================
echo   vBot - QQ机器人启动脚本
echo ======================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo [信息] Python版本:
python --version
echo.

REM 检查依赖
echo [信息] 检查依赖...
pip show botpy >nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [信息] 依赖已就绪
echo.
echo ======================================
echo   正在启动 vBot...
echo ======================================
echo.

python bot.py

pause
