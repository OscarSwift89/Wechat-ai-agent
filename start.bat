@echo off
chcp 65001 >nul
title 小红书自动运营系统

echo.
echo ========================================
echo 小红书自动运营系统
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查配置文件是否存在
if not exist "config.yaml" (
    echo ❌ 配置文件不存在，正在运行安装向导...
    python install.py
    if errorlevel 1 (
        echo ❌ 安装失败，请检查错误信息
        pause
        exit /b 1
    )
)

echo ✅ 环境检查通过
echo.
echo 🚀 启动小红书自动运营系统...
echo 提示: 按 Ctrl+C 可以随时中断执行
echo.

REM 运行主程序
python run.py

echo.
echo 程序执行完成
pause 