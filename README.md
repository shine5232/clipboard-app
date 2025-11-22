# 📋 剪贴板助手 (Clipboard Helper)

一个简洁高效的 Windows 剪贴板增强工具，支持多项复制和批量粘贴。

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## ✨ 主要特性

- 🔥 **自动收集** - 所有复制的内容自动保存到列表
- ⚡ **一键粘贴** - `Ctrl+Space` 批量粘贴所有收集的内容
- 🎨 **精美界面** - 现代化渐变色悬浮窗设计
- 💾 **持久化存储** - 数据自动保存，重启后恢复
- 🪟 **置顶显示** - 窗口始终保持在最前
- 🎯 **全局快捷键** - 任意应用中使用
- 🔔 **系统托盘** - 最小化到托盘，不占用任务栏
- 🛡️ **智能去重** - 自动过滤重复内容

---

## 🚀 快速开始

### 方法一：使用可执行文件（推荐）

1. 下载 `ClipboardHelper.exe`
2. 双击运行
3. 开始使用！

### 方法二：从源码运行

```bash
# 1. 克隆或下载项目
cd E:\clipboard-app

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python main.py
```

---

## ⌨️ 快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl+C` | 复制内容 | 复制的内容自动添加到列表 |
| **`Ctrl+Space`** | **批量粘贴** | 将列表中所有内容用逗号拼接后自动粘贴 |
| `Ctrl+Shift+C` | 显示/隐藏窗口 | 切换窗口显示状态 |
| `Ctrl+Shift+Q` | 退出程序 | 关闭应用程序 |

---

## 📖 使用说明

### 📥 基本使用流程

```
1️⃣ 正常复制内容（Ctrl+C）
   ↓
2️⃣ 内容自动添加到列表
   ↓
3️⃣ 重复步骤1-2，收集多条内容
   ↓
4️⃣ 按 Ctrl+Space 一键粘贴所有内容
```

### 💡 使用示例

**场景：收集多个手机号码**

```
复制：138****1234  → 列表显示：138****1234
复制：139****5678  → 列表显示：138****1234, 139****5678
复制：136****9012  → 列表显示：138****1234, 139****5678, 136****9012

按 Ctrl+Space → 自动粘贴：138****1234,139****5678,136****9012
```

### 🎛️ 窗口管理

| 操作 | 方法 |
|------|------|
| 删除单条记录 | 点击右侧 `×` 按钮 |
| 清空所有记录 | 点击顶部 🗑️ 按钮 |
| 折叠/展开窗口 | 点击 `−` 或 `+` 按钮 |
| 拖动窗口位置 | 按住顶部渐变区域拖动 |
| 最小化到托盘 | 点击 `×` 关闭按钮 |
| 恢复窗口 | 双击托盘图标或按 `Ctrl+Shift+C` |

---

## 🖼️ 界面预览

```
┌─────────────────────────────────────┐
│  剪贴板 (3)              − 🗑️ ×     │ ← 渐变色顶栏
├─────────────────────────────────────┤
│  138****1234        12:30:45    ×  │
│  139****5678        12:31:12    ×  │
│  136****9012        12:32:05    ×  │
└─────────────────────────────────────┘
```

**特点**：
- 🎨 紫蓝渐变色顶栏
- ⏰ 每条记录显示时间戳
- 🗑️ 快捷删除按钮
- 📏 自动省略过长文本

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| **PyQt5** | GUI 界面框架 |
| **win32clipboard** | 剪贴板读写（带重试机制） |
| **pynput** | 全局快捷键监听 |
| **ctypes** | Windows API 调用（SendInput） |
| **json** | 数据持久化存储 |

---

## 📦 打包说明

### 快速打包

```bash
# 方法一：使用脚本（最简单）
双击运行 build.bat

# 方法二：使用快速脚本
双击运行 quick_build.bat

# 方法三：手动打包
pip install pyinstaller
pyinstaller --name=ClipboardHelper --onefile --windowed main.py
```

### 打包结果

打包后文件位置：`dist\ClipboardHelper.exe`

**文件说明**：
- 大小：约 30-50 MB
- 类型：单文件可执行程序
- 依赖：无需 Python 环境
- 分发：仅需这一个 exe 文件

### 打包选项说明

| 选项 | 说明 |
|------|------|
| `--onefile` | 打包成单个 exe 文件 |
| `--windowed` | 窗口模式，不显示控制台 |
| `--name` | 指定输出文件名 |
| `--noconfirm` | 覆盖旧文件无需确认 |

---

## 📋 依赖项

```txt
PyQt5>=5.15.0
pywin32>=300
pynput>=1.7.0
```

安装命令：
```bash
pip install -r requirements.txt
```

---

## ⚙️ 配置说明

### 数据存储

**存储位置**：`data/clipboard_data.json`

**数据格式**：
```json
[
  {
    "text": "复制的文本内容",
    "timestamp": "12:30:45"
  }
]
```

### 自定义配置

可修改 `main.py` 中的参数：

| 配置项 | 位置 | 默认值 | 说明 |
|--------|------|--------|------|
| 窗口大小 | 第 334 行 | `(360, 560)` | 宽度 × 高度 |
| 窗口位置 | 第 336 行 | 右下角 | 屏幕坐标 |
| 轮询间隔 | 第 210 行 | `300ms` | 剪贴板检查频率 |
| 粘贴分隔符 | 第 286 行 | `,` | 拼接符号 |
| 忽略时间 | 第 293 行 | `1.5s` | 粘贴后忽略窗口 |
| 比对时间 | 第 141 行 | `3.0s` | 粘贴内容比对窗口 |

**示例：修改分隔符**
```python
# 第 286 行
combined_text = ','.join(texts)  # 改成 '\n'.join(texts) 用换行分隔
```

---

## ❓ 常见问题 FAQ

### Q1: 为什么打包后文件这么大（30-50MB）？
**A**: 这是正常现象。PyInstaller 会将 Python 解释器和所有依赖库打包进去，确保在没有 Python 环境的电脑上也能运行。

### Q2: 杀毒软件报毒怎么办？
**A**: 这是**误报**。PyInstaller 打包的文件经常被误判。解决方法：
- 添加到杀毒软件的信任列表
- 或从源码运行：`python main.py`

### Q3: 快捷键 Ctrl+Space 不生效？
**A**: 可能的原因：
1. 程序未运行（检查托盘图标）
2. 与输入法冲突（某些输入法占用此快捷键）
3. 解决：修改快捷键为其他组合

### Q4: 如何更改粘贴分隔符？
**A**: 编辑 `main.py` 第 286 行：
```python
# 逗号分隔（默认）
combined_text = ','.join(texts)

# 换行分隔
combined_text = '\n'.join(texts)

# 空格分隔
combined_text = ' '.join(texts)

# 自定义分隔符
combined_text = ' | '.join(texts)
```

### Q5: 能否支持图片、文件等非文本内容？
**A**: 当前版本仅支持纯文本。后续版本可能会添加更多类型支持。

### Q6: 如何设置开机自启动？
**A**:
1. 右键 `ClipboardHelper.exe` → 创建快捷方式
2. 按 `Win+R` 输入 `shell:startup` → 回车
3. 将快捷方式复制到启动文件夹

### Q7: 数据会自动保存吗？
**A**: 是的！每次添加或删除内容都会自动保存到 `data/clipboard_data.json`，重启程序后自动恢复。

---

## 🐛 已知问题与限制

### 已知问题

1. **多行文本拆分**
   - 现象：复制多行文本时会按换行拆分成多条记录
   - 原因：`process_clipboard_text()` 方法设计如此
   - 影响：保留此功能，便于逐行处理

2. **粘贴延迟**
   - 现象：某些应用中粘贴有约 250ms 延迟
   - 原因：等待剪贴板更新和用户释放按键
   - 影响：轻微，确保粘贴成功

3. **快捷键冲突**
   - 现象：Ctrl+Space 可能与输入法冲突
   - 解决：修改代码中的快捷键组合

### 限制说明

- ✅ 仅支持纯文本（不支持图片、文件）
- ✅ Windows 平台专用
- ✅ 需要管理员权限注册全局快捷键

---

## 🔄 更新日志

### v3.0.0 (2024-01-XX) - 稳定版

#### ✨ 新增功能
- ✅ 自动收集剪贴板内容
- ✅ **快捷键改为 Ctrl+Space**（避免冲突）
- ✅ 批量粘贴功能（自动模拟 Ctrl+V）
- ✅ 精美的渐变色悬浮窗界面
- ✅ 系统托盘支持
- ✅ 数据持久化存储
- ✅ 全局快捷键支持

#### 🚀 优化改进
- ✅ 剪贴板访问增加 3 次重试机制
- ✅ 改进异常处理（打印具体错误信息）
- ✅ 优化粘贴时间窗口逻辑（1.5s 忽略 + 3s 比对）
- ✅ 修复列表遍历删除问题（使用列表推导式）
- ✅ 删除所有未使用的死代码
- ✅ 清理未使用的导入和常量

#### 🐛 Bug 修复
- ✅ 修复 `last_pasted_text` 永不清理的问题
- ✅ 修复粘贴内容可能被重复添加的问题
- ✅ 修复在某些应用中快捷键冲突的问题

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/clipboard-helper.git
cd clipboard-helper

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行测试
python main.py
```

### 代码规范

- 使用 4 空格缩进
- 遵循 PEP 8 规范
- 添加必要的注释
- 提交前测试所有功能

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

感谢以下开源项目：

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 强大的 GUI 框架
- [pynput](https://github.com/moses-palmer/pynput) - 全局快捷键支持
- [PyInstaller](https://www.pyinstaller.org/) - Python 打包工具
- [pywin32](https://github.com/mhammond/pywin32) - Windows API 绑定

---

## 📞 支持与反馈

如有问题或建议，请：
1. 提交 [Issue](https://github.com/yourusername/clipboard-helper/issues)
2. 发送邮件至：your.email@example.com
3. 查看 [BUILD_GUIDE.txt](BUILD_GUIDE.txt) 获取打包帮助

---

## 📊 项目结构

```
clipboard-app/
├── main.py                    # 主程序
├── requirements.txt           # Python 依赖
├── build.bat                  # 完整打包脚本
├── quick_build.bat            # 快速打包脚本
├── BUILD_GUIDE.txt            # 打包指南
├── README.md                  # 本文档
└── data/
    └── clipboard_data.json    # 数据存储（自动生成）
```

---

## 🌟 特性对比

| 功能 | Chrome 扩展 | 本桌面版 |
|------|------------|---------|
| 自动收集 | ✅ | ✅ |
| 跨应用使用 | ❌ 仅浏览器 | ✅ **全局** |
| 粘贴方式 | 右键菜单 | **Ctrl+Space（一键）** |
| 快捷键 | ❌ | ✅ 全局快捷键 |
| 数据持久化 | ✅ | ✅ |
| 系统托盘 | ❌ | ✅ |
| 独立运行 | ❌ 依赖浏览器 | ✅ |

**桌面版优势**：
- ✅ 不限于浏览器，**任何应用**都能使用
- ✅ 全局快捷键，**一键粘贴**
- ✅ 独立运行，不依赖浏览器
- ✅ 性能更好，资源占用低

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**

---

<div align="center">
Made with ❤️
</div>
