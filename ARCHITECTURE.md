# 剪贴板助手 - 架构文档

## 目录
- [概述](#概述)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [架构设计](#架构设计)
- [核心模块](#核心模块)
- [数据流](#数据流)
- [主要功能](#主要功能)

---

## 概述

剪贴板助手是一个基于 PyQt5 开发的 Windows 桌面应用程序，采用 MVC（Model-View-Controller）架构模式，实现了剪贴板内容的智能管理和批量操作功能。

### 设计原则
- **分层架构**：清晰的 UI、业务逻辑、数据模型分层
- **模块化设计**：各模块职责明确，低耦合高内聚
- **可扩展性**：支持主题扩展、功能插件化
- **用户体验优先**：流畅的动画、直观的交互

---

## 技术栈

### 核心框架
- **PyQt5**: GUI 框架
- **Python 3.14**: 主要开发语言

### 关键技术
- **QPropertyAnimation**: 实现流畅的动画效果
- **Windows API**: 剪贴板监听和窗口管理
- **pynput**: 全局快捷键监听
- **JSON**: 配置和数据持久化

---

## 项目结构

```
clipboard-app/
├── main.py                          # 应用程序入口
├── models/                          # 数据模型层
│   ├── __init__.py
│   └── data_model.py               # 数据持久化模型
├── services/                        # 业务逻辑层
│   ├── __init__.py
│   └── clipboard_service.py        # 剪贴板业务逻辑
├── ui/                             # UI 层
│   ├── __init__.py
│   └── components/                 # UI 组件
│       ├── __init__.py
│       ├── floating_icon.py        # 浮动图标/胶囊组件
│       ├── tray_menu.py            # 系统托盘菜单
│       ├── clipboard_delegate.py   # 列表项委托渲染
│       ├── gradient_header.py      # 渐变标题栏
│       ├── clickable_label.py      # 可点击标签
│       └── capsule_widget.py       # 胶囊组件（旧版）
├── utils/                          # 工具模块
│   ├── __init__.py
│   ├── clipboard_utils.py          # 剪贴板工具
│   ├── clipboard_listener.py       # 剪贴板监听器
│   ├── keyboard_simulator.py       # 键盘模拟
│   ├── window_manager.py           # 窗口管理
│   └── data_manager.py             # 数据管理（旧版）
├── themes/                         # 主题模块
│   ├── __init__.py
│   └── theme_manager.py            # 主题管理器
├── README.md                       # 项目说明
└── ARCHITECTURE.md                 # 架构文档（本文档）
```

---

## 架构设计

### MVC 架构模式

```
┌─────────────────────────────────────────────────────────┐
│                        View Layer                        │
│  ┌────────────────┐  ┌─────────────────────────────┐   │
│  │  ClipboardWindow│  │   UI Components              │   │
│  │  (main.py)     │  │   - FloatingIcon             │   │
│  │                │  │   - TrayMenu                 │   │
│  │                │  │   - ClipboardItemDelegate    │   │
│  └────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     Controller Layer                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │         ClipboardService (Business Logic)        │   │
│  │  - handle_clipboard_change()                     │   │
│  │  - prepare_paste_content()                       │   │
│  │  - set_output_mode()                             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      Model Layer                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           DataModel (Data Persistence)           │   │
│  │  - save_clipboard_data()                         │   │
│  │  - load_clipboard_data()                         │   │
│  │  - save_settings()                               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 模块职责

#### View Layer (视图层)
- **ClipboardWindow**: 主窗口，负责 UI 渲染和用户交互
- **UI Components**: 可复用的 UI 组件
  - `FloatingIcon`: 胶囊模式的浮动图标
  - `TrayMenu`: 系统托盘菜单
  - `ClipboardItemDelegate`: 列表项的自定义渲染

#### Controller Layer (控制层)
- **ClipboardService**: 剪贴板业务逻辑
  - 处理剪贴板变化
  - 管理数据列表
  - 准备粘贴内容
  - 执行粘贴操作

#### Model Layer (模型层)
- **DataModel**: 数据持久化
  - 保存/加载剪贴板数据
  - 保存/加载用户设置

---

## 核心模块

### 1. main.py - 主窗口模块

**职责**: 应用程序入口，主窗口管理

**关键类**:
- `ClipboardWindow`: 主窗口类
- `SettingsDialog`: 设置对话框

**核心功能**:
- 初始化 UI 和各层组件
- 管理胶囊模式切换
- 处理用户交互事件
- 全局快捷键注册

**关键方法**:
```python
def enter_capsule_mode(self):
    """进入胶囊模式：主界面缩小并飞到屏幕右侧"""

def restore_from_capsule(self):
    """从胶囊模式恢复：胶囊放大并飞回原位置"""

def on_clipboard_changed(self):
    """处理剪贴板变化事件"""
```

---

### 2. services/clipboard_service.py - 业务逻辑层

**职责**: 剪贴板数据处理和业务逻辑

**关键类**:
- `ClipboardService`: 剪贴板业务逻辑服务

**核心功能**:
- 剪贴板内容去重和验证
- 输出模式管理（逗号拼接/顺序/倒序）
- 准备和执行粘贴操作
- 前一个窗口管理

**数据结构**:
```python
clipboard_data = [
    {
        'text': '复制内容',
        'timestamp': '12:34:56'
    }
]
```

**信号**:
- `data_changed`: 数据变化信号
- `notification_requested`: 通知请求信号

---

### 3. models/data_model.py - 数据模型层

**职责**: 数据持久化和存储管理

**核心功能**:
- 保存/加载剪贴板数据（临时）
- 保存/加载用户设置（持久）
- 应用退出时清理临时数据

**存储位置**:
```
Windows: C:\Users\<用户名>\AppData\Roaming\ClipboardHelper\
├── clipboard_data.json    # 剪贴板数据（临时）
└── settings.json          # 用户设置（持久）
```

**配置结构**:
```json
{
    "output_mode": "comma",      // 输出模式
    "theme": "light",            // 主题
    "color_scheme": "pure_blue"  // 配色方案
}
```

---

### 4. ui/components/ - UI 组件模块

#### 4.1 floating_icon.py - 浮动图标组件

**职责**: 胶囊模式的浮动图标

**核心功能**:
- 显示圆形图标或胶囊状态
- 显示主窗口截图（用于动画）
- 处理鼠标交互（悬停、双击）
- 变形动画支持

**状态切换**:
```
主窗口截图 → 缩小动画 → 胶囊状态
胶囊状态 → 放大动画 → 主窗口截图 → 主窗口
```

#### 4.2 tray_menu.py - 托盘菜单组件

**职责**: 系统托盘自定义菜单

**核心功能**:
- 无边框渐变菜单
- 主题切换支持
- 菜单项悬停效果

#### 4.3 clipboard_delegate.py - 列表委托

**职责**: 列表项的自定义渲染

**核心功能**:
- 虚拟化渲染优化性能
- 悬停高亮效果
- 删除按钮交互
- 文本截断和省略

---

### 5. utils/ - 工具模块

#### 5.1 clipboard_listener.py - 剪贴板监听器

**职责**: 监听 Windows 剪贴板变化

**实现方式**:
- Windows API (AddClipboardFormatListener)
- 备用轮询机制

#### 5.2 clipboard_utils.py - 剪贴板工具

**职责**: 剪贴板读写操作

**核心功能**:
- 读取剪贴板文本
- 写入剪贴板文本

#### 5.3 keyboard_simulator.py - 键盘模拟

**职责**: 模拟键盘操作

**核心功能**:
- 模拟 Ctrl+V 粘贴

#### 5.4 window_manager.py - 窗口管理

**职责**: Windows 窗口操作

**核心功能**:
- 获取前台窗口
- 设置前台窗口
- 窗口激活

---

### 6. themes/theme_manager.py - 主题管理器

**职责**: 应用主题和样式管理

**支持主题**:
- 日间模式 (light)
- 暗夜模式 (dark)

**支持配色**:
- 魅力蓝 (blue_gradient)
- 天空蓝 (pure_blue)
- 青草绿 (pure_green)
- 樱花粉 (sakura_pink)

**样式组件**:
- 容器样式
- 列表样式
- 按钮样式
- 标题栏样式
- 下拉框样式

---

## 数据流

### 1. 剪贴板监听流程

```
用户复制内容 (Ctrl+C)
    ↓
Windows 剪贴板变化
    ↓
ClipboardListener 检测到变化
    ↓
触发 clipboard_changed 信号
    ↓
ClipboardWindow.on_clipboard_changed()
    ↓
ClipboardService.handle_clipboard_change()
    ↓
验证、去重、添加数据
    ↓
触发 data_changed 信号
    ↓
ClipboardWindow.update_list()
    ↓
UI 更新显示
```

### 2. 批量粘贴流程

```
用户按下快捷键 (Ctrl+Space)
    ↓
GlobalHotKeys 触发
    ↓
ClipboardWindow.do_paste()
    ↓
ClipboardService.prepare_paste_content()
    ↓
根据输出模式拼接内容
    ↓
写入剪贴板
    ↓
延迟 250ms
    ↓
ClipboardService.execute_paste()
    ↓
模拟 Ctrl+V
    ↓
内容粘贴到目标应用
```

### 3. 胶囊模式切换流程

```
用户双击标题栏
    ↓
ClipboardWindow.header_double_click()
    ↓
ClipboardWindow.enter_capsule_mode()
    ↓
1. 保存窗口位置
2. 对主窗口截图
3. 创建 FloatingIcon
4. 设置截图到 FloatingIcon
5. 隐藏主窗口
6. 执行缩小飞出动画 (500ms)
7. 80% 时切换为胶囊状态
8. 启用鼠标悬停
    ↓
用户鼠标悬停胶囊
    ↓
FloatingIcon 触发 mouse_entered 信号
    ↓
ClipboardWindow.restore_from_capsule()
    ↓
1. 禁用鼠标悬停
2. 执行放大飞入动画 (500ms)
3. 20% 时切换为截图模式
4. 80% 时显示主窗口
5. 完成后隐藏 FloatingIcon
```

---

## 主要功能

### 1. 剪贴板管理
- ✅ 自动捕获 Ctrl+C 复制内容
- ✅ 自动去重
- ✅ 时间戳记录
- ✅ 单项删除
- ✅ 一键清空

### 2. 批量粘贴
- ✅ 逗号拼接模式
- ✅ 顺序输出模式
- ✅ 倒序输出模式
- ✅ 快捷键粘贴 (Ctrl+Space)

### 3. 胶囊模式
- ✅ 双击标题栏进入胶囊模式
- ✅ 主界面缩小动画
- ✅ 飞到屏幕右侧
- ✅ 鼠标悬停自动恢复
- ✅ 位置记忆

### 4. 主题系统
- ✅ 日间/暗夜模式
- ✅ 4 种配色方案
- ✅ 实时主题切换
- ✅ 主题持久化

### 5. 系统集成
- ✅ 系统托盘图标
- ✅ 自定义托盘菜单
- ✅ 全局快捷键
- ✅ 窗口置顶
- ✅ 单实例运行

### 6. 性能优化
- ✅ 虚拟化列表渲染
- ✅ 截图缓存复用
- ✅ 平滑动画优化
- ✅ 内存占用优化

---

## 扩展指南

### 添加新的输出模式

1. 在 `ClipboardService` 添加新模式逻辑
2. 在 `SettingsDialog` 添加选项
3. 在 `ClipboardWindow.update_mode_label()` 添加标识

### 添加新的主题配色

1. 在 `theme_manager.py` 的 `get_color_scheme_colors()` 添加配色
2. 在 `SettingsDialog` 添加选项

### 添加新的 UI 组件

1. 在 `ui/components/` 创建组件文件
2. 继承 `QWidget` 或其他 Qt 组件
3. 在 `main.py` 中导入和使用

---

## 性能考虑

### 优化策略
1. **虚拟化渲染**: 使用 `QStyledItemDelegate` 实现列表虚拟化
2. **截图缓存**: 进入胶囊模式时缓存截图，复用于飞入动画
3. **动画优化**: 使用 `QPropertyAnimation` 硬件加速
4. **信号机制**: 使用 Qt 信号避免轮询

### 内存管理
- 退出时清理临时数据
- 动画引用保存在对象属性避免垃圾回收
- 截图在动画完成后及时清理

---

## 安全考虑

### 数据安全
- 剪贴板数据不持久化到磁盘（退出即清理）
- 配置文件存储在用户目录
- 不记录敏感信息

### 单实例保护
- 使用 Windows 互斥量确保只有一个实例运行
- 防止重复启动导致资源冲突

---

## 未来规划

### 功能扩展
- [ ] 支持图片剪贴板
- [ ] 支持富文本格式
- [ ] 云同步功能
- [ ] 搜索和过滤
- [ ] 分组管理

### 技术优化
- [ ] 插件系统
- [ ] 配置导入导出
- [ ] 多语言支持
- [ ] 跨平台支持

---

## 维护建议

### 代码规范
- 遵循 PEP 8 编码规范
- 使用类型注解
- 添加文档字符串
- 保持模块职责单一

### 测试建议
- 测试剪贴板监听稳定性
- 测试动画流畅度
- 测试内存占用
- 测试异常场景

### 版本管理
- 使用语义化版本号
- 保持向后兼容
- 记录变更日志

---

*最后更新: 2025-11-27*
