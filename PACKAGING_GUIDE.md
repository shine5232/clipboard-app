# 剪贴板助手 - macOS 打包与安装指南

> 本文档详细说明如何将「剪贴板助手」打包为 macOS 安装包，以及如何在 macOS 系统中安装和使用。

---

## 目录

- [项目概览](#项目概览)
- [环境准备](#环境准备)
- [打包方案](#打包方案)
  - [方案一：PyInstaller（推荐）](#方案一pyinstaller推荐)
  - [方案二：py2app](#方案二py2app)
- [制作 DMG 安装镜像](#制作-dmg-安装镜像)
- [安装与使用](#安装与使用)
  - [安装步骤](#安装步骤)
  - [系统权限授予](#系统权限授予)
  - [基本使用](#基本使用)
- [代码签名与公证（可选）](#代码签名与公证可选)
- [常见问题与故障排除](#常见问题与故障排除)
- [附录：项目结构与依赖](#附录项目结构与依赖)

---

## 项目概览

| 项目 | 说明 |
|------|------|
| **应用名称** | 剪贴板助手 (Clipboard Helper) |
| **类型** | macOS 桌面 GUI 应用 |
| **语言** | Python 3.9+ |
| **GUI 框架** | PyQt5 5.15+ |
| **目标平台** | macOS 10.14 (Mojave) 及以上 |
| **架构** | MVC (Model-View-Controller) |
| **Bundle ID** | com.clipboardhelper.app |

### 核心功能

- 自动捕获 `Cmd+C` 复制的文本，存储剪贴板历史
- 三种批量粘贴模式：逗号拼接、顺序输出 (FIFO)、倒序输出 (LIFO)
- 浮动胶囊模式，拖拽到屏幕边缘自动收缩
- 菜单栏应用，隐藏 Dock 图标
- 全局快捷键支持
- 日间/暗夜主题，4 种配色方案

---

## 环境准备

### 1. 系统要求

- macOS 10.14 (Mojave) 或更高版本
- Python 3.9 ~ 3.12（建议，3.13+ 可能存在兼容性问题）
- Xcode Command Line Tools

> **重要提示**：必须在 macOS 上进行打包。PyInstaller 和 py2app 生成平台特定的二进制文件，无法在 Windows 上交叉编译 macOS 应用。

### 2. 安装 Xcode 命令行工具

```bash
xcode-select --install
```

### 3. 创建虚拟环境（推荐）

```bash
cd /path/to/clipboard-app-mac

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 4. 安装项目依赖

```bash
pip3 install -r requirements.txt
```

依赖清单：

```
# 通用依赖
PyQt5>=5.15.0          # GUI 框架
pynput>=1.7.6          # 键盘模拟
pyperclip>=1.8.2       # 剪贴板操作（备用）

# macOS 特定依赖
pyobjc-core>=9.0               # macOS 原生 API 桥接
pyobjc-framework-Cocoa>=9.0    # AppKit（窗口管理）
pyobjc-framework-Quartz>=9.0   # 全局快捷键、事件处理

# 打包工具
PyInstaller>=6.0.0     # 生成独立可执行文件
```

---

## 打包方案

### 方案一：PyInstaller（推荐）

PyInstaller 将 Python 应用及其所有依赖打包为一个独立的 `.app` 应用包，用户无需安装 Python 环境即可使用。

#### 一键打包（使用脚本）

```bash
# 赋予脚本执行权限
chmod +x build_mac.sh

# 执行打包
./build_mac.sh
```

脚本会自动完成：检查 Python 环境 → 安装 PyInstaller → 安装依赖 → 执行打包。

#### 手动打包

```bash
# 安装 PyInstaller
pip3 install pyinstaller

# 执行打包命令
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
```

#### 参数说明

| 参数 | 说明 |
|------|------|
| `--name` | 输出应用名称 |
| `--windowed` | 创建 .app 应用包（不显示终端窗口） |
| `--onefile` | 打包为单个文件 |
| `--add-data "src:dst"` | 包含额外数据文件（源路径:目标路径） |
| `--osx-bundle-identifier` | macOS 应用 Bundle ID |
| `--hidden-import` | 显式包含隐式导入的模块 |

#### 打包产出

```
dist/剪贴板助手.app    ← macOS 应用包，可直接双击运行
```

---

### 方案二：py2app

py2app 是 macOS 专用的 Python 应用打包工具，项目中已配置 `setup.py`。

#### 开发模式（快速测试）

```bash
# 安装 py2app
pip3 install py2app

# 以别名模式构建（不复制文件，用于快速测试）
python3 setup.py py2app -A
```

#### 正式打包

```bash
# 清理旧的构建产物
rm -rf build dist

# 正式打包
python3 setup.py py2app
```

#### 打包产出

```
dist/剪贴板助手.app    ← macOS 应用包
```

#### py2app 配置说明（setup.py）

项目 `setup.py` 中已配置以下关键参数：

| 配置项 | 值 | 说明 |
|--------|------|------|
| `CFBundleName` | 剪贴板助手 | 应用名称 |
| `CFBundleIdentifier` | com.clipboardhelper.app | 唯一标识符 |
| `CFBundleVersion` | 1.0.0 | 版本号 |
| `LSUIElement` | True | 隐藏 Dock 图标（菜单栏应用） |
| `NSHighResolutionCapable` | True | 支持 Retina 显示屏 |
| `NSRequiresAquaSystemAppearance` | False | 支持深色模式 |

---

## 制作 DMG 安装镜像

将 `.app` 打包为 `.dmg` 安装镜像是 macOS 最标准的分发格式，用户可以通过拖拽安装。

### 方法一：使用 hdiutil（macOS 自带）

```bash
# 创建临时目录
mkdir -p dmg_temp

# 复制 app 到临时目录
cp -R "dist/剪贴板助手.app" dmg_temp/

# 创建 Applications 文件夹的快捷方式
ln -s /Applications dmg_temp/Applications

# 生成 DMG
hdiutil create -volname "剪贴板助手" \
               -srcfolder dmg_temp \
               -ov -format UDZO \
               "dist/剪贴板助手.dmg"

# 清理临时目录
rm -rf dmg_temp
```

### 方法二：使用 create-dmg（更美观）

```bash
# 安装 create-dmg
brew install create-dmg

# 生成带自定义窗口布局的 DMG
create-dmg \
    --volname "剪贴板助手" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "剪贴板助手.app" 175 190 \
    --app-drop-link 425 190 \
    "dist/剪贴板助手.dmg" \
    "dist/剪贴板助手.app"
```

### 最终分发文件

```
dist/剪贴板助手.dmg    ← 分发给用户的安装镜像
```

---

## 安装与使用

### 安装步骤

1. **双击 `剪贴板助手.dmg`** 挂载磁盘镜像
2. **拖拽 `剪贴板助手.app` 到 `Applications` 文件夹**
3. **首次打开应用**：
   - 在启动台（Launchpad）或 `Applications` 文件夹中找到应用
   - **右键点击** → 选择 **"打开"**
   - 在弹窗中点击 **"打开"**（绕过 Gatekeeper 安全检查）

> 首次运行必须通过右键菜单打开，直接双击会被 Gatekeeper 阻止（因为应用未签名）。之后可以正常双击打开。

### 系统权限授予

应用首次运行后，需要在 **系统设置** 中手动授予以下权限，否则核心功能无法正常工作：

| 权限 | 设置路径 | 用途 |
|------|----------|------|
| **辅助功能** | 系统设置 → 隐私与安全性 → 辅助功能 | 全局快捷键监听、模拟键盘按键 |
| **输入监控** | 系统设置 → 隐私与安全性 → 输入监控 | pynput 监听键盘事件 |

授权步骤：

1. 打开 **系统设置** → **隐私与安全性**
2. 分别进入 **辅助功能** 和 **输入监控**
3. 点击左下角 🔒 锁图标解锁
4. 点击 **"+"** 按钮，添加 `剪贴板助手.app`
5. 确保其旁边的开关为 **开启** 状态

### 基本使用

#### 启动

- 应用启动后出现在 **菜单栏**（屏幕顶部状态栏），不会出现在 Dock 中
- 菜单栏右键点击图标可显示菜单

#### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Cmd+V` | 批量粘贴所有已收集的内容 |
| `Cmd+Shift+C` | 显示/隐藏主窗口 |
| `Cmd+Shift+Q` | 退出程序 |

#### 操作流程

1. 在任意应用中使用 `Cmd+C` 复制文本 → 应用自动捕获
2. 重复复制多条内容
3. 按 `Ctrl+Cmd+V` → 根据当前输出模式粘贴内容

#### 三种输出模式

| 模式 | 说明 | 示例 |
|------|------|------|
| **逗号拼接** | 所有内容用逗号连接，一次性粘贴 | `apple,banana,cherry` |
| **顺序输出 (FIFO)** | 按复制顺序，每次粘贴一条 | 第1次→apple, 第2次→banana, 第3次→cherry |
| **倒序输出 (LIFO)** | 按倒序，每次粘贴一条 | 第1次→cherry, 第2次→banana, 第3次→apple |

#### 胶囊模式

- 将窗口拖拽到屏幕边缘 → 自动收缩为胶囊悬浮窗
- 鼠标悬停到胶囊上 → 自动展开恢复主窗口

#### 数据存储位置

```
~/Library/Application Support/ClipboardHelper/
├── clipboard_data.json    # 剪贴板数据（退出时自动清除，保护隐私）
└── settings.json          # 用户设置（持久保存）
```

---

## 代码签名与公证（可选）

如果需要将应用分发给其他用户，建议进行代码签名和公证，避免 Gatekeeper 阻止运行。

### 前提条件

- Apple Developer ID（$99/年），注册地址：https://developer.apple.com

### 签名步骤

```bash
# 1. 查看可用的签名证书
security find-identity -v -p codesigning

# 2. 对 .app 进行签名
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name (TEAM_ID)" \
    "dist/剪贴板助手.app"

# 3. 验证签名
codesign --verify --deep --strict "dist/剪贴板助手.app"
```

### 公证步骤（Notarization）

```bash
# 1. 将 app 压缩为 zip
ditto -c -k --keepParent "dist/剪贴板助手.app" "dist/剪贴板助手.zip"

# 2. 提交公证
xcrun notarytool submit "dist/剪贴板助手.zip" \
    --apple-id "your@email.com" \
    --team-id "TEAM_ID" \
    --password "app-specific-password" \
    --wait

# 3. 公证通过后，装订票据到 app
xcrun stapler staple "dist/剪贴板助手.app"
```

> 完成签名和公证后，用户双击即可直接打开应用，不会出现安全警告。

---

## 常见问题与故障排除

### Q1: 打包失败，提示 ModuleNotFoundError

**原因**：PyInstaller 未能自动检测到某些隐式导入的模块。

**解决方案**：在打包命令中添加 `--hidden-import` 参数：

```bash
pyinstaller --hidden-import "PyQt5.sip" \
            --hidden-import "pynput.keyboard._darwin" \
            --hidden-import "pynput.mouse._darwin" \
            ...
```

### Q2: 打包后的 app 双击无反应

**排查方法**：在终端中直接运行 app 查看错误信息：

```bash
# PyInstaller 打包的 app
./dist/剪贴板助手.app/Contents/MacOS/剪贴板助手

# 或查看系统日志
log show --predicate 'process == "剪贴板助手"' --last 5m
```

### Q3: Gatekeeper 阻止运行（"无法打开应用，因为无法验证开发者"）

**解决方案**：

1. 系统设置 → 隐私与安全性 → 通用 → 点击 "仍然允许"
2. 或右键点击 app → 选择 "打开" → 在弹窗中点击 "打开"
3. 或使用终端命令移除隔离属性：
   ```bash
   xattr -cr /Applications/剪贴板助手.app
   ```

### Q4: 全局快捷键不生效

**原因**：未授予辅助功能权限。

**解决方案**：系统设置 → 隐私与安全性 → 辅助功能 → 添加并启用「剪贴板助手」。

### Q5: 打包后的 app 体积较大（50-80MB）

**原因**：这是正常的。PyInstaller 将完整的 Python 解释器和所有依赖库（PyQt5、pyobjc 等）打包在内。

**优化方法**：
- 使用虚拟环境打包，避免包含不必要的库
- 在 `setup.py` 或 spec 文件中配置 `excludes` 排除不需要的模块
- 使用 UPX 压缩（`--upx-dir /path/to/upx`）

### Q6: py2app 打包报错 "No module named ..."

**解决方案**：在 `setup.py` 的 `OPTIONS.packages` 中显式添加缺失的模块：

```python
OPTIONS = {
    'packages': ['PyQt5', 'pynput', 'pyobjc'],
    'includes': ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    ...
}
```

---

## 附录：项目结构与依赖

### 项目结构

```
clipboard-app-mac/
├── main.py                    # 应用入口（含主窗口和设置对话框）
├── models/
│   └── data_model.py          # 数据持久化层（JSON 存储）
├── services/
│   └── clipboard_service.py   # 业务逻辑（剪贴板操作管理）
├── ui/
│   └── components/
│       ├── floating_icon.py   # 浮动胶囊组件
│       ├── tray_menu.py       # 系统托盘菜单
│       ├── clipboard_delegate.py  # 列表项渲染
│       ├── gradient_header.py # 渐变标题栏
│       ├── clickable_label.py # 可点击标签
│       └── capsule_widget.py  # 胶囊组件
├── utils/
│   ├── clipboard_utils.py     # 剪贴板读写工具
│   ├── clipboard_listener.py  # 剪贴板变化监听
│   ├── keyboard_simulator.py  # 键盘模拟（pynput）
│   ├── window_manager.py      # macOS 窗口管理（AppKit）
│   └── data_manager.py        # 数据管理工具
├── themes/
│   └── theme_manager.py       # 主题/样式管理
├── data/
│   └── settings.json          # 用户设置
├── setup.py                   # py2app 打包配置
├── build_mac.sh               # PyInstaller 打包脚本
├── ClipboardHelper.spec       # PyInstaller spec 文件
├── requirements.txt           # Python 依赖列表
└── README.md                  # 项目说明
```

### 依赖关系图

```
应用程序
├── PyQt5 >= 5.15.0            # GUI 界面、剪贴板读写、动画
├── pynput >= 1.7.6            # 键盘模拟（模拟粘贴操作）
├── pyperclip >= 1.8.2         # 剪贴板操作（备用方案）
├── pyobjc-core >= 9.0         # macOS 原生 API 桥接
├── pyobjc-framework-Cocoa     # AppKit（窗口管理、应用激活）
└── pyobjc-framework-Quartz    # 全局快捷键、事件监听
```

### 完整打包流程总结

```
源代码 (.py)
    │
    ├── PyInstaller ──→ 剪贴板助手.app
    │   或
    └── py2app ────────→ 剪贴板助手.app
                              │
                         hdiutil / create-dmg
                              │
                         剪贴板助手.dmg  ← 分发给用户
                              │
                    用户双击 DMG → 拖拽到 Applications → 运行
```

---

*文档版本: 1.0 | 最后更新: 2025-02*
