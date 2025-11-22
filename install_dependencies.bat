@echo off
chcp 65001 >nul
echo ========================================
echo 安装剪贴板助手依赖
echo ========================================
echo.

echo [1/3] 检查 Python...
python --version
if errorlevel 1 (
    echo ❌ 错误：未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)
echo.

echo [2/3] 卸载旧的 keyboard 库（如果有）...
pip uninstall keyboard -y
echo.

echo [3/3] 安装所有依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo.
    echo ⚠ 国内镜像安装失败，尝试官方源...
    pip install -r requirements.txt
)
echo.

echo ========================================
echo ✅ 安装完成！
echo ========================================
echo.
echo 已安装的包：
pip list | findstr "pynput pyperclip PyQt5"
echo.
echo 现在可以运行程序了：
echo   python main.py
echo.
pause
