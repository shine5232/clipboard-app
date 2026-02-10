# Windows 剪贴板助手 -> macOS 迁移指南

## 项目概述

将 Windows 版剪贴板助手迁移到 macOS 平台。当前版本使用 PyQt5 构建，包含多个 Windows 特定的 API 调用需要替换。

---

## 迁移任务清单

### 阶段一：环境准备

- [ ] **1.1 安装 macOS 开发环境**
  - 安装 Python 3.9+ (推荐使用 Homebrew: `brew install python@3.11`)
  - 安装 PyQt5: `pip install PyQt5`
  - 安装 macOS 特定依赖

- [x] **1.2 更新 requirements.txt** ✅ 已完成
  ```
  # 通用依赖
  PyQt5>=5.15.0
  pynput>=1.7.6
  pyperclip>=1.8.2

  # macOS 特定依赖
  pyobjc-core>=9.0
  pyobjc-framework-Cocoa>=9.0
  pyobjc-framework-Quartz>=9.0

  # 打包工具
  py2app>=0.28.0
  # 或继续使用 PyInstaller
  PyInstaller>=6.0.0
  ```

- [ ] **1.3 创建 macOS 专用分支**
  ```bash
  git checkout -b macos-port
  ```

---

### 阶段二：核心模块迁移

#### 2.1 剪贴板工具模块 (`utils/clipboard_utils.py`)

- [x] **2.1.1 替换 win32clipboard 为跨平台方案** ✅ 已完成

  **当前代码问题：**
  - 使用 `win32clipboard` 模块（Windows 专用）
  - 使用 `win32con.CF_UNICODETEXT` 常量

  **解决方案：** 使用 PyQt5 自带的剪贴板 API 或 pyperclip

  ```python
  # macOS 版本 - utils/clipboard_utils.py
  """
  剪贴板工具模块 - macOS 版本
  使用 PyQt5 QClipboard 或 pyperclip
  """

  import time
  from PyQt5.QtWidgets import QApplication
  from PyQt5.QtCore import QMimeData


  def get_clipboard_text():
      """获取剪贴板文本"""
      max_retries = 3
      retry_delay = 0.05

      for attempt in range(max_retries):
          try:
              clipboard = QApplication.clipboard()
              text = clipboard.text()
              return text if text else None
          except Exception:
              if attempt < max_retries - 1:
                  time.sleep(retry_delay)
      return None


  def set_clipboard_text(text):
      """设置剪贴板文本"""
      max_retries = 3
      retry_delay = 0.05

      for attempt in range(max_retries):
          try:
              clipboard = QApplication.clipboard()
              clipboard.setText(text)
              return True
          except Exception:
              if attempt < max_retries - 1:
                  time.sleep(retry_delay)
      return False


  # process_clipboard_text 函数无需修改（纯 Python 逻辑）
  ```

---

#### 2.2 剪贴板监听器 (`utils/clipboard_listener.py`)

- [x] **2.2.1 移除 Windows API 调用** ✅ 已完成

  **当前代码问题：**
  - 使用 `ctypes.windll.user32`
  - 使用 `AddClipboardFormatListener` Windows API
  - 使用 `WM_CLIPBOARDUPDATE` 消息

  **解决方案：** 使用 PyQt5 的 `QClipboard.dataChanged` 信号

  ```python
  # macOS 版本 - utils/clipboard_listener.py
  """
  剪贴板监听器 - macOS 版本
  使用 PyQt5 QClipboard 信号
  """

  from PyQt5.QtWidgets import QApplication
  from PyQt5.QtCore import QObject, pyqtSignal


  class ClipboardListener(QObject):
      """
      剪贴板监听器 - 跨平台版本
      使用 Qt 的剪贴板变化信号
      """

      clipboard_changed = pyqtSignal()

      def __init__(self, parent=None):
          super().__init__(parent)
          self._running = False
          self._clipboard = None

      def start(self):
          """开始监听剪贴板"""
          if self._running:
              return True

          try:
              self._clipboard = QApplication.clipboard()
              self._clipboard.dataChanged.connect(self._on_clipboard_changed)
              self._running = True
              return True
          except Exception:
              return False

      def stop(self):
          """停止监听剪贴板"""
          if not self._running:
              return

          try:
              if self._clipboard:
                  self._clipboard.dataChanged.disconnect(self._on_clipboard_changed)
          except Exception:
              pass

          self._running = False

      def _on_clipboard_changed(self):
          """剪贴板内容变化时的回调"""
          self.clipboard_changed.emit()
  ```

---

#### 2.3 键盘模拟器 (`utils/keyboard_simulator.py`)

- [x] **2.3.1 替换 Windows SendInput API** ✅ 已完成

  **当前代码问题：**
  - 使用 `ctypes.windll.user32.SendInput`
  - 使用 Windows 虚拟键码

  **解决方案：** 使用 pynput 或 pyobjc 的 Quartz 框架

  ```python
  # macOS 版本 - utils/keyboard_simulator.py
  """
  键盘模拟模块 - macOS 版本
  使用 pynput 进行跨平台键盘模拟
  """

  import time
  from pynput.keyboard import Key, Controller

  keyboard = Controller()


  def simulate_paste():
      """
      模拟 Cmd+V 粘贴操作 (macOS)
      """
      try:
          # 先释放所有修饰键
          for key in [Key.cmd, Key.alt, Key.shift, Key.ctrl]:
              try:
                  keyboard.release(key)
              except:
                  pass

          time.sleep(0.05)

          # 模拟 Cmd+V
          with keyboard.pressed(Key.cmd):
              keyboard.press('v')
              keyboard.release('v')

          return True
      except Exception:
          return False


  def simulate_key_combo(*keys, hold_time=0.02):
      """
      模拟组合键操作

      Args:
          *keys: pynput Key 或字符列表
          hold_time: 按键保持时间
      """
      try:
          # 按下所有键
          for key in keys:
              keyboard.press(key)
              time.sleep(hold_time)

          # 释放所有键（逆序）
          for key in reversed(keys):
              keyboard.release(key)
              time.sleep(hold_time)

          return True
      except Exception:
          return False


  def release_all_modifiers():
      """释放所有修饰键"""
      for key in [Key.cmd, Key.alt, Key.shift, Key.ctrl]:
          try:
              keyboard.release(key)
          except:
              pass
  ```

---

#### 2.4 窗口管理器 (`utils/window_manager.py`)

- [x] **2.4.1 替换 Windows 窗口 API** ✅ 已完成

  **当前代码问题：**
  - 使用 `ctypes.windll.user32.GetForegroundWindow`
  - 使用 `ctypes.windll.user32.SetForegroundWindow`

  **解决方案：** 使用 pyobjc 的 AppKit/Quartz 框架

  ```python
  # macOS 版本 - utils/window_manager.py
  """
  窗口管理模块 - macOS 版本
  使用 pyobjc 访问 macOS 窗口 API
  """

  import time

  try:
      from AppKit import NSWorkspace, NSRunningApplication
      from Quartz import (
          CGWindowListCopyWindowInfo,
          kCGWindowListOptionOnScreenOnly,
          kCGNullWindowID,
          kCGWindowOwnerPID,
          kCGWindowLayer
      )
      HAS_MACOS_API = True
  except ImportError:
      HAS_MACOS_API = False


  def get_foreground_window():
      """
      获取当前活动应用程序

      Returns:
          NSRunningApplication 或 None
      """
      if not HAS_MACOS_API:
          return None

      try:
          workspace = NSWorkspace.sharedWorkspace()
          active_app = workspace.frontmostApplication()
          return active_app
      except Exception:
          return None


  def set_foreground_window(app):
      """
      激活指定应用程序

      Args:
          app: NSRunningApplication 对象

      Returns:
          bool: 是否成功
      """
      if not HAS_MACOS_API or not app:
          return False

      try:
          app.activateWithOptions_(0)  # NSApplicationActivateIgnoringOtherApps
          return True
      except Exception:
          return False


  class WindowFocusManager:
      """窗口焦点管理器"""

      def __init__(self):
          self.previous_app = None

      def save_current_window(self):
          """保存当前活动应用"""
          self.previous_app = get_foreground_window()
          return bool(self.previous_app)

      def restore_previous_window(self, wait_time=0.1):
          """恢复之前的应用焦点"""
          if not self.previous_app:
              return False

          success = set_foreground_window(self.previous_app)

          if wait_time > 0:
              time.sleep(wait_time)

          return success

      def get_previous_window(self):
          """获取之前保存的应用"""
          return self.previous_app
  ```

---

#### 2.5 数据模型 (`models/data_model.py`)

- [x] **2.5.1 替换 Windows 注册表访问** ✅ 已完成

  **当前代码问题：**
  - 使用 `winreg` 检测系统主题
  - 使用 `APPDATA` 环境变量

  **解决方案：** 使用 macOS 的 defaults 命令或 pyobjc

  ```python
  # macOS 版本中需要修改的部分

  import os
  import subprocess
  from pathlib import Path


  class DataModel:
      def __init__(self, data_dir=None):
          if data_dir is None:
              # macOS: 使用 ~/Library/Application Support/
              data_dir = Path.home() / 'Library' / 'Application Support' / 'ClipboardHelper'
          else:
              data_dir = Path(data_dir)

          self.data_dir = data_dir
          self.data_file = data_dir / 'clipboard_data.json'
          self.settings_file = data_dir / 'settings.json'

          self.data_dir.mkdir(parents=True, exist_ok=True)

      @staticmethod
      def detect_system_theme():
          """
          检测 macOS 系统主题

          Returns:
              str: 'light' 或 'dark'
          """
          try:
              result = subprocess.run(
                  ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                  capture_output=True,
                  text=True
              )
              # 如果返回 "Dark"，则为深色模式
              if result.returncode == 0 and 'Dark' in result.stdout:
                  return 'dark'
              return 'light'
          except Exception:
              return 'light'
  ```

---

### 阶段三：主程序修改 (`main.py`)

- [x] **3.1 修改单实例检查** ✅ 已完成

  ```python
  # macOS 版本 - 使用文件锁或端口检查
  import socket
  import sys

  def check_single_instance():
      """检查是否已有实例运行 (macOS)"""
      try:
          # 使用端口绑定方式检测
          sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          sock.bind(('127.0.0.1', 47632))  # 使用固定端口
          # 不关闭 socket，保持绑定状态
          return sock  # 返回 socket 对象保持引用
      except socket.error:
          # 端口已被占用，说明已有实例运行
          from PyQt5.QtWidgets import QMessageBox
          app = QApplication(sys.argv)
          QMessageBox.information(
              None,
              '提示',
              '剪贴板助手已经在运行中！\n\n请在菜单栏查看图标。'
          )
          return None
  ```

- [x] **3.2 修改快捷键配置** ✅ 已完成

  ```python
  # macOS 使用 Command 键代替 Ctrl
  self.hotkey_listener = GlobalHotKeys({
      '<cmd>+<space>': on_paste_hotkey,      # Cmd+Space 粘贴
      '<cmd>+<shift>+c': on_toggle_hotkey,   # Cmd+Shift+C 显示/隐藏
      '<cmd>+<shift>+q': on_quit_hotkey      # Cmd+Shift+Q 退出
  })
  ```

  **注意：** `Cmd+Space` 与 macOS Spotlight 冲突，建议改为其他组合键：
  ```python
  '<cmd>+<ctrl>+v': on_paste_hotkey,  # Cmd+Ctrl+V 粘贴
  ```

- [x] **3.3 修改窗口标志** ✅ 已完成

  ```python
  # macOS 窗口标志调整
  self.setWindowFlags(
      Qt.WindowStaysOnTopHint |
      Qt.FramelessWindowHint |
      Qt.Tool  # 保持 Tool 标志，在 macOS 上也有效
  )
  ```

- [x] **3.4 移除 Windows 特定代码** ✅ 已完成

  需要删除/修改的代码：
  - `import ctypes` 中的 Windows 相关调用
  - `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID`
  - 单实例检查中的 `CreateMutexW`

---

### 阶段四：UI 适配

- [ ] **4.1 调整字体**

  macOS 默认使用 SF Pro 字体，需要调整字体设置：
  ```python
  # 在主题管理器中添加平台检测
  import platform

  def get_default_font():
      if platform.system() == 'Darwin':
          return '-apple-system, BlinkMacSystemFont, "SF Pro Text"'
      return 'Microsoft YaHei, SimHei'
  ```

- [ ] **4.2 调整系统托盘**

  macOS 使用菜单栏图标，行为与 Windows 系统托盘略有不同：
  - 单击显示菜单（而非双击）
  - 图标尺寸应为 22x22 或 44x44 (Retina)

- [x] **4.3 适配 Retina 显示屏** ✅ 已完成

  ```python
  # 在 main.py 开头添加
  from PyQt5.QtCore import Qt
  from PyQt5.QtWidgets import QApplication

  # 启用高 DPI 支持
  QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
  QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
  ```

---

### 阶段五：打包与分发

- [ ] **5.1 创建 macOS 打包脚本**

  **方案 A: 使用 PyInstaller**
  ```bash
  # build_mac.sh
  #!/bin/bash
  pyinstaller --name "剪贴板助手" \
              --windowed \
              --icon=icon.icns \
              --add-data "themes:themes" \
              --add-data "ui:ui" \
              --osx-bundle-identifier "com.clipboardhelper.app" \
              main.py
  ```

  **方案 B: 使用 py2app**
  ```python
  # setup.py
  from setuptools import setup

  APP = ['main.py']
  DATA_FILES = []
  OPTIONS = {
      'argv_emulation': True,
      'iconfile': 'icon.icns',
      'plist': {
          'CFBundleName': '剪贴板助手',
          'CFBundleDisplayName': '剪贴板助手',
          'CFBundleIdentifier': 'com.clipboardhelper.app',
          'LSUIElement': True,  # 隐藏 Dock 图标
      },
      'packages': ['PyQt5'],
  }

  setup(
      app=APP,
      data_files=DATA_FILES,
      options={'py2app': OPTIONS},
      setup_requires=['py2app'],
  )
  ```

  运行打包：
  ```bash
  python setup.py py2app
  ```

- [ ] **5.2 创建应用图标**

  需要创建 `.icns` 格式图标文件：
  ```bash
  # 从 PNG 创建 icns
  mkdir icon.iconset
  sips -z 16 16 icon.png --out icon.iconset/icon_16x16.png
  sips -z 32 32 icon.png --out icon.iconset/icon_16x16@2x.png
  sips -z 32 32 icon.png --out icon.iconset/icon_32x32.png
  sips -z 64 64 icon.png --out icon.iconset/icon_32x32@2x.png
  sips -z 128 128 icon.png --out icon.iconset/icon_128x128.png
  sips -z 256 256 icon.png --out icon.iconset/icon_128x128@2x.png
  sips -z 256 256 icon.png --out icon.iconset/icon_256x256.png
  sips -z 512 512 icon.png --out icon.iconset/icon_256x256@2x.png
  sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png
  sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
  iconutil -c icns icon.iconset
  ```

- [ ] **5.3 代码签名（可选）**

  如需分发，需要进行 Apple 代码签名：
  ```bash
  codesign --deep --force --verify --verbose \
           --sign "Developer ID Application: Your Name" \
           "dist/剪贴板助手.app"
  ```

---

### 阶段六：测试验证

- [ ] **6.1 功能测试**
  - [ ] 剪贴板监听是否正常工作
  - [ ] 快捷键是否正确响应
  - [ ] 批量粘贴功能是否正常
  - [ ] 窗口显示/隐藏是否正常
  - [ ] 系统托盘/菜单栏图标是否正常
  - [ ] 主题切换是否正常
  - [ ] 数据持久化是否正常

- [ ] **6.2 兼容性测试**
  - [ ] macOS 12 (Monterey) 测试
  - [ ] macOS 13 (Ventura) 测试
  - [ ] macOS 14 (Sonoma) 测试
  - [ ] Intel Mac 测试
  - [ ] Apple Silicon (M1/M2/M3) 测试

- [ ] **6.3 性能测试**
  - [ ] 内存占用监控
  - [ ] CPU 使用率监控
  - [ ] 启动时间测试

---

## 文件修改汇总

| 文件路径 | 修改类型 | 主要变更 |
|---------|---------|---------|
| `requirements.txt` | 修改 | 添加 pyobjc，移除 pywin32 |
| `utils/clipboard_utils.py` | 重写 | 使用 PyQt5 QClipboard |
| `utils/clipboard_listener.py` | 重写 | 使用 Qt 信号替代 Windows API |
| `utils/keyboard_simulator.py` | 重写 | 使用 pynput |
| `utils/window_manager.py` | 重写 | 使用 pyobjc AppKit |
| `models/data_model.py` | 修改 | 修改数据目录和主题检测 |
| `main.py` | 修改 | 单实例检查、快捷键、窗口标志 |
| `themes/theme_manager.py` | 修改 | 调整默认字体 |
| `build_mac.sh` | 新建 | macOS 打包脚本 |
| `setup.py` | 新建 | py2app 配置 |

---

## 注意事项

1. **权限问题**：macOS 需要授予应用辅助功能权限才能监听全局快捷键和模拟键盘输入
   - 系统偏好设置 → 安全性与隐私 → 隐私 → 辅助功能

2. **Gatekeeper**：未签名的应用首次运行时会被阻止
   - 用户需要在系统偏好设置中允许运行

3. **沙盒限制**：如果需要上架 Mac App Store，需要适配沙盒限制

4. **快捷键冲突**：避免使用与系统快捷键冲突的组合（如 Cmd+Space）

---

## 参考资源

- [PyQt5 文档](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [pyobjc 文档](https://pyobjc.readthedocs.io/)
- [pynput 文档](https://pynput.readthedocs.io/)
- [py2app 文档](https://py2app.readthedocs.io/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/macos)
