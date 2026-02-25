# 剪贴板助手 📋

> 一个功能强大、界面美观的 macOS 剪贴板增强工具

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

---

## ✨ 核心特性

### 🎯 主要功能
- **自动捕获** - 自动监听 Cmd+C 复制操作，智能记录剪贴板内容
- **批量粘贴** - 支持多种输出模式：逗号拼接、顺序输出、倒序输出
- **胶囊模式** - 创新的交互体验，拖拽到屏幕边缘自动收缩为胶囊悬浮窗
- **快捷操作** - 全局快捷键支持，随时随地快速操作
- **智能去重** - 自动过滤重复内容，保持列表整洁

### 🎨 界面设计
- **精美主题** - 支持日间/暗夜模式，4 种配色方案可选
- **自动适配** - 自动检测 macOS 系统主题（深色/浅色）
- **流畅动画** - 丝滑的过渡动画和交互反馈
- **现代UI** - 无边框设计、渐变效果、圆角阴影
- **Retina 支持** - 完美支持高分辨率显示屏

### 🔧 系统集成
- **菜单栏图标** - 最小化到菜单栏，不占用 Dock
- **自定义菜单** - 精美的菜单栏右键菜单
- **单实例运行** - 防止重复启动
- **窗口置顶** - 始终显示在最前方

---

## 🚀 快速开始

### 环境要求

- **操作系统**: macOS 10.14 (Mojave) 或更高版本
- **Python**: 3.9 或更高版本
- **依赖库**: PyQt5, pynput, pyobjc

### 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：
```bash
pip install PyQt5 pynput pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz
```

### 运行程序

```bash
python main.py
```

### 权限设置

首次运行时，macOS 会提示需要授予以下权限：

1. **辅助功能权限** - 用于全局快捷键监听
   - 系统偏好设置 → 安全性与隐私 → 隐私 → 辅助功能
   - 添加终端或 Python 应用

2. **自动化权限** - 用于模拟键盘输入
   - 系统会自动提示，点击"允许"即可

---

## 📖 使用指南

### 基础操作

#### 1. 复制内容
- 在任意应用中使用 `Cmd+C` 复制内容
- 剪贴板助手会自动捕获并记录
- 重复内容会自动去重

#### 2. 批量粘贴
- 按下全局快捷键 `Ctrl+Cmd+V`

#### 3. 输出模式
- **逗号拼接**: 将所有内容用逗号连接后粘贴
- **顺序输出**: 按添加顺序依次粘贴（每次快捷键粘贴一条）
- **倒序输出**: 按添加倒序依次粘贴（每次快捷键粘贴一条）

### 胶囊模式

#### 进入胶囊模式
- **拖拽到边缘** - 将窗口拖拽到屏幕边缘（左/右/上/下）并释放
- **双击标题栏** - 主窗口会缩小并飞到屏幕右侧成为胶囊状悬浮窗
- 胶囊会记住主窗口的原始位置

#### 恢复主窗口
- **鼠标悬停** - 将鼠标移动到胶囊上，会自动飞回并展开主窗口
- **双击胶囊** - 双击胶囊也可以恢复主窗口

#### 使用场景
- 需要多次复制粘贴时，使用胶囊模式不遮挡工作区域
- 临时隐藏窗口但又想快速调出

### 全局快捷键

| 快捷键 | 功能 |
|-------|------|
| `Ctrl+Cmd+V` | 批量粘贴 |
| `Cmd+Shift+C` | 显示/隐藏主窗口 |
| `Cmd+Shift+Q` | 退出程序 |

### 菜单栏图标

- **单击图标**: 无操作
- **双击图标**: 显示/隐藏主窗口
- **右键图标**: 显示菜单
  - 显示窗口
  - 退出程序

---

## 🖼️ 界面预览

### 日间模式
```
┌─────────────────────────────────────┐
│  剪贴板 (3)       拼 🗑️ ⚙️ ×        │ ← 渐变色顶栏
├─────────────────────────────────────┤
│  138****1234        12:30:45    ×  │
│  139****5678        12:31:12    ×  │
│  136****9012        12:32:05    ×  │
└─────────────────────────────────────┘
```

### 暗夜模式
```
┌─────────────────────────────────────┐
│  剪贴板 (3)       顺 🗑️ ⚙️ ×        │ ← 深色渐变顶栏
├─────────────────────────────────────┤
│  138****1234        12:30:45    ×  │ ← 深色背景
│  139****5678        12:31:12    ×  │
│  136****9012        12:32:05    ×  │
└─────────────────────────────────────┘
```

**界面特点**：
- 🎨 紫蓝/深灰渐变色顶栏（根据主题）
- 📊 实时显示输出模式标识
- ⏰ 每条记录显示时间戳
- 🗑️ 快捷删除按钮
- 📏 自动省略过长文本
- ⚙️ 设置按钮快速访问

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| **PyQt5** | GUI 界面框架 |
| **QClipboard** | 剪贴板读写 |
| **pynput** | 键盘模拟 |
| **pyobjc (Quartz)** | 全局快捷键监听、macOS 原生 API 调用 |
| **json** | 数据持久化存储 |

---

## 📦 打包说明

### 快速打包

```bash
# 方法一：使用脚本（推荐）
chmod +x build_mac.sh
./build_mac.sh

# 方法二：使用 PyInstaller
pip install pyinstaller
pyinstaller --name="剪贴板助手" --windowed --onefile main.py

# 方法三：使用 py2app（生成 .app 包）
pip install py2app
python setup.py py2app
```

### 打包结果

- **PyInstaller**: `dist/剪贴板助手` (可执行文件)
- **py2app**: `dist/剪贴板助手.app` (macOS 应用包)

**文件说明**：
- 类型：macOS 应用程序
- 依赖：无需 Python 环境
- 分发：仅需应用程序文件

### 注意事项

1. 首次运行需要在"系统偏好设置 → 安全性与隐私"中允许运行
2. 需要授予辅助功能权限才能使用全局快捷键

---

## 📋 依赖项

```txt
PyQt5>=5.15.0
pynput>=1.7.6
pyperclip>=1.8.2
pyobjc-core>=9.0
pyobjc-framework-Cocoa>=9.0
pyobjc-framework-Quartz>=9.0
PyInstaller>=6.0.0
```

安装命令：
```bash
pip install -r requirements.txt
```

---

## ⚙️ 配置说明

### 输出模式

在设置中可以选择三种输出模式：

1. **逗号拼接模式**
   ```
   复制: "apple", "banana", "cherry"
   粘贴: apple,banana,cherry
   ```

2. **顺序输出模式**
   ```
   第一次 Ctrl+Cmd+V: apple
   第二次 Ctrl+Cmd+V: banana
   第三次 Ctrl+Cmd+V: cherry
   ```

3. **倒序输出模式**
   ```
   第一次 Ctrl+Cmd+V: cherry
   第二次 Ctrl+Cmd+V: banana
   第三次 Ctrl+Cmd+V: apple
   ```

### 主题设置

#### 系统主题
- **日间模式**: 明亮清新的浅色主题
- **暗夜模式**: 护眼舒适的深色主题
- **自动检测**: 默认跟随 macOS 系统主题

#### 配色方案
- **魅力蓝** (blue_gradient): 蓝紫渐变，神秘优雅
- **天空蓝** (pure_blue): 清新蓝色，清爽明快
- **青草绿** (pure_green): 自然绿色，清新护眼
- **樱花粉** (sakura_pink): 浪漫粉色，温柔可爱

### 数据存储

应用数据存储在用户目录：
```
~/Library/Application Support/ClipboardHelper/
├── clipboard_data.json    # 剪贴板数据（临时，退出时清除）
└── settings.json          # 用户设置（持久保存）
```

**注意**: 出于隐私考虑，剪贴板数据在程序退出时会自动清除，下次启动时从空白状态开始。

---

## 🏗️ 项目结构

```
clipboard-app-mac/
├── main.py                 # 应用入口
├── models/                 # 数据模型层
│   └── data_model.py
├── services/               # 业务逻辑层
│   └── clipboard_service.py
├── ui/                     # UI 层
│   └── components/         # UI 组件
│       ├── floating_icon.py
│       ├── tray_menu.py
│       └── clipboard_delegate.py
├── utils/                  # 工具模块
│   ├── clipboard_utils.py
│   ├── clipboard_listener.py
│   ├── keyboard_simulator.py
│   └── window_manager.py
├── themes/                 # 主题管理
│   └── theme_manager.py
├── setup.py               # py2app 打包配置
├── build_mac.sh           # 打包脚本
├── requirements.txt       # 依赖列表
└── README.md              # 项目说明（本文档）
```

---

## 🔧 开发指南

### 技术栈

- **GUI 框架**: PyQt5
- **动画引擎**: QPropertyAnimation
- **剪贴板**: Qt QClipboard
- **快捷键**: pyobjc Quartz Event Tap (pynput 备用)
- **窗口管理**: pyobjc (AppKit)

### 架构设计

采用 MVC（Model-View-Controller）架构：

- **Model**: `DataModel` - 数据持久化
- **View**: `ClipboardWindow` 及 UI 组件 - 界面展示
- **Controller**: `ClipboardService` - 业务逻辑

---

## ❓ 常见问题 FAQ

### Q1: 三种输出模式有什么区别？

**A**:
- **逗号拼接**：所有内容用逗号连接，一次性粘贴
- **顺序输出**：从第一条开始，每次粘贴一条（FIFO）
- **倒序输出**：从最后一条开始，每次粘贴一条（LIFO）

### Q2: 如何切换主题？

**A**: 点击设置按钮（齿轮图标）→ 选择"系统主题" → 选择"日间模式"或"暗夜模式" → 点击"应用"或"确定"

### Q3: 快捷键不生效？

**A**: 可能的原因：
1. 程序未运行（检查菜单栏图标）
2. 未授予辅助功能权限（系统偏好设置 → 安全性与隐私 → 隐私 → 辅助功能）
3. 与其他应用快捷键冲突
4. 剪贴板列表为空

### Q4: 如何设置开机自启动？

**A**:
1. 系统偏好设置 → 用户与群组 → 登录项
2. 点击 "+" 添加剪贴板助手应用

### Q5: 程序启动提示已在运行？

**A**: 检查菜单栏是否已有程序图标，或使用活动监视器结束 Python 进程。

### Q6: Gatekeeper 阻止运行？

**A**: 如果提示"无法打开应用，因为无法验证开发者"：
1. 系统偏好设置 → 安全性与隐私 → 通用
2. 点击"仍然允许"

---

## 🐛 已知问题与限制

### 已知问题

1. **需要辅助功能权限**
   - 现象：全局快捷键不工作
   - 解决：在系统偏好设置中授予权限

2. **粘贴延迟**
   - 现象：粘贴有约 250ms 延迟
   - 原因：等待剪贴板更新和用户释放按键
   - 影响：轻微，确保粘贴成功

### 限制说明

- ✅ 仅支持纯文本（不支持图片、文件）
- ✅ macOS 平台专用
- ✅ 需要辅助功能权限

---

## 📝 版本历史

### v1.0.0-mac (2025-02)
- 🍎 macOS 版本首次发布
- ✅ 完整的剪贴板管理功能
- ✅ 胶囊模式（边缘吸附/双击标题栏）
- ✅ 主题系统（日间/暗夜模式 + 4种配色）
- ✅ 自动检测 macOS 系统主题
- ✅ 全局快捷键 (Ctrl+Cmd+V, Cmd+Shift+C, Cmd+Shift+Q)
- ✅ 菜单栏集成
- ✅ Retina 显示屏支持
- ✅ 使用 pyobjc 进行原生 macOS API 调用

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 添加必要的注释和文档字符串
- 保持代码简洁清晰
- 测试新功能确保稳定性

---

## 📄 开源协议

本项目采用 MIT 协议开源。详见 [LICENSE](LICENSE) 文件。

---

## 👨‍💻 作者

**LZ**

如有问题或建议，欢迎通过以下方式联系：

- 💬 Issues: [GitHub Issues](https://github.com/yourusername/clipboard-app/issues)

---

## 🙏 致谢

感谢以下开源项目：

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 强大的 Python GUI 框架
- [pynput](https://github.com/moses-palmer/pynput) - 全局快捷键监听
- [pyobjc](https://github.com/ronaldoussoren/pyobjc) - macOS 原生 API 支持

---

<p align="center">
  Made with ❤️ for macOS
</p>

<p align="center">
  <sub>如果你喜欢这个项目，别忘了给它一个 ⭐️</sub>
</p>
