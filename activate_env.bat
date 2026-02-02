@echo off
REM 激活 conda 环境并打开终端
REM 双击此文件将打开 cmd 终端并自动激活 qwen3-tts 环境

REM 获取脚本所在目录（项目根目录）
cd /d "%~dp0"

REM 检查 conda 是否可用
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 conda 命令
    echo 请确保已安装 Anaconda 或 Miniconda，并将其添加到系统 PATH
    pause
    exit /b 1
)

REM 初始化 conda（如果未初始化，静默执行）
call conda init cmd.exe >nul 2>&1

REM 激活 conda 环境
call conda activate qwen3-tts

REM 检查环境是否激活成功
if %errorlevel% neq 0 (
    echo 警告: 无法激活 conda 环境 qwen3-tts
    echo 请确保环境已创建: conda create -n qwen3-tts
    echo.
)

REM 显示当前目录和环境信息
echo.
echo ========================================
echo 项目目录: %CD%
echo Conda 环境: qwen3-tts
echo ========================================
echo.

REM 保持终端打开，可以继续输入命令
cmd /k
