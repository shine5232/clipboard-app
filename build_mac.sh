#!/bin/bash
# macOS 打包脚本
# 使用 PyInstaller 将剪贴板助手打包为 macOS 应用

echo "=== 剪贴板助手 macOS 打包脚本 ==="
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查 PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "正在安装 PyInstaller..."
    pip3 install pyinstaller
fi

# 安装依赖
echo "正在安装依赖..."
pip3 install -r requirements.txt

# 创建打包
echo ""
echo "正在打包应用..."
pyinstaller --name "剪贴板助手" \
            --windowed \
            --onefile \
            --add-data "themes:themes" \
            --add-data "ui:ui" \
            --add-data "utils:utils" \
            --add-data "models:models" \
            --add-data "services:services" \
            --osx-bundle-identifier "com.clipboardhelper.app" \
            --hidden-import "PyQt5.sip" \
            main.py

echo ""
echo "=== 打包完成 ==="
echo "应用程序位于: dist/剪贴板助手.app"
echo ""
echo "注意事项:"
echo "1. 首次运行需要在系统偏好设置中授予辅助功能权限"
echo "2. 如果遇到 Gatekeeper 阻止，请在系统偏好设置 > 安全性与隐私 中允许运行"
