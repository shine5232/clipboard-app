# 模块化重构指南

## 📦 已创建的模块

项目已成功提取以下模块，可以在 `main.py` 中引用使用：

### 工具模块 (utils/)

1. **clipboard_utils.py** - 剪贴板工具
2. **keyboard_simulator.py** - 键盘模拟器
3. **window_manager.py** - 窗口管理器
4. **data_manager.py** - 数据管理器

### 主题模块 (themes/)

5. **theme_manager.py** - 主题管理器

### UI组件 (ui/components/)

6. **gradient_header.py** - 渐变标题栏组件
7. **clickable_label.py** - 可点击标签组件

---

## 🔧 如何在 main.py 中使用

### 1. 导入模块

在 `main.py` 顶部添加导入语句：

```python
# 工具模块
from utils.clipboard_utils import get_clipboard_text, set_clipboard_text, process_clipboard_text
from utils.keyboard_simulator import simulate_paste, send_input_key, VK_CONTROL, VK_SHIFT, VK_MENU, VK_V
from utils.window_manager import get_foreground_window, set_foreground_window
from utils.data_manager import ClipboardDataManager

# 主题模块
from themes.theme_manager import ThemeManager, get_color_scheme_colors

# UI组件
from ui.components.gradient_header import GradientHeader
from ui.components.clickable_label import ClickableLabel
```

### 2. 替换现有代码

#### 剪贴板操作
**替换前:**
```python
def get_clipboard_text():
    max_retries = 3
    # ... 50行代码
```

**替换后:**
```python
# 直接使用导入的函数
text = get_clipboard_text()
set_clipboard_text("新文本")
texts = process_clipboard_text(multi_line_text)
```

#### 数据管理
**替换前:**
```python
def load_data(self):
    try:
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                # ... 20行代码
```

**替换后:**
```python
# 在 __init__ 中
self.data_manager = ClipboardDataManager()

# 加载数据
self.clipboard_data = self.data_manager.load_clipboard_data()
self.settings = self.data_manager.load_settings()

# 保存数据
self.data_manager.save_clipboard_data(self.clipboard_data)
self.data_manager.save_settings(self.settings)
```

#### 主题管理
**替换前:**
```python
# 在各个地方重复定义样式
label.setStyleSheet("""
    QLabel {
        background: transparent;
        color: #303133;
        # ... 很多行
    }
""")
```

**替换后:**
```python
# 在 __init__ 中创建主题管理器
self.theme_manager = ThemeManager(
    theme=self.settings.get('theme', 'light'),
    color_scheme=self.settings.get('color_scheme', 'pure_blue')
)

# 使用主题管理器设置样式
label.setStyleSheet(self.theme_manager.get_label_style(font_size=13))
time_label.setStyleSheet(self.theme_manager.get_time_label_style())
delete_btn.setStyleSheet(self.theme_manager.get_delete_button_style())
```

#### 渐变标题栏
**替换前:**
```python
def create_header(self):
    # 定义 HeaderWidget 类
    class HeaderWidget(QWidget):
        def __init__(self, parent=None):
            # ... 50行代码
        def paintEvent(self, event):
            # ... 30行代码

    header = HeaderWidget()
    # ... 设置布局和按钮
    return header
```

**替换后:**
```python
def create_header(self):
    # 创建渐变标题栏
    header = GradientHeader(title='剪贴板 (0)', height=50, parent=self)
    header.setDarkMode(self.theme_manager.is_dark)
    header.setColorScheme(self.theme_manager.color_scheme)

    # 启用拖拽
    header.enableDragging()

    # 添加按钮
    header.addCustomButton('拼', '当前输出模式', None)
    header.addCustomButton('🗑', '清空剪贴板', self.clear_clipboard)
    header.addCustomButton('⚙', '设置', self.show_settings)
    header.addCloseButton(self.hide_window)

    return header
```

#### 可点击标签
**替换前:**
```python
class ClickableLabel(QLabel):
    def __init__(self, text, parent_window, paste_text):
        super().__init__(text)
        self.parent_window = parent_window
        self.paste_text = paste_text

    def mousePressEvent(self, event):
        # ... 代码
```

**替换后:**
```python
# 导入组件
from ui.components.clickable_label import ClickableLabel

# 创建可点击标签
label = ClickableLabel(
    text=text,
    callback=self.paste_single_item,
    data=text
)
label.setWordWrap(False)
label.setFixedWidth(200)
label.setStyleSheet(self.theme_manager.get_label_style())
```

#### 键盘模拟
**替换前:**
```python
def _execute_single_paste(self):
    try:
        send_input_key(VK_CONTROL, up=True)
        send_input_key(VK_MENU, up=True)
        # ... 20行代码
```

**替换后:**
```python
def _execute_single_paste(self):
    from utils.keyboard_simulator import simulate_paste
    simulate_paste()
```

#### 窗口管理
**替换前:**
```python
def show_window(self):
    try:
        user32 = ctypes.windll.user32
        self.previous_window = user32.GetForegroundWindow()
        # ... 代码
```

**替换后:**
```python
def show_window(self):
    self.previous_window = get_foreground_window()
    print(f"[DEBUG] Recorded previous window: {self.previous_window}")
    self.show()
    self.activateWindow()
    self.raise_()

def paste_single_item(self, text):
    # ... 设置剪贴板
    self.hide()

    # 激活前一个窗口
    if self.previous_window:
        set_foreground_window(self.previous_window)
        time.sleep(0.1)
```

---

## 📊 代码减少统计

| 功能模块 | 原代码行数 | 重构后 | 减少行数 |
|---------|----------|--------|---------|
| 剪贴板操作 | ~80行 | ~10行 | 70行 |
| 数据管理 | ~60行 | ~15行 | 45行 |
| 主题样式 | ~250行 | ~30行 | 220行 |
| 渐变标题栏 | ~150行 | ~10行 | 140行 |
| 键盘模拟 | ~100行 | ~5行 | 95行 |
| 窗口管理 | ~40行 | ~8行 | 32行 |
| **总计** | **~680行** | **~78行** | **~600行** |

**main.py 可以减少约 600 行代码！**

---

## ✅ 重构的好处

1. **代码复用** - 模块可在其他项目中直接使用
2. **易于维护** - 修改样式只需改一处
3. **清晰架构** - 职责分明，逻辑清晰
4. **易于测试** - 每个模块可独立测试
5. **扩展性强** - 添加新主题/功能更容易

---

## 📝 下一步建议

### 立即可做的重构

1. **main.py 顶部添加导入语句**
2. **替换剪贴板操作函数** (最容易，风险最小)
3. **替换数据管理代码** (独立性强)
4. **引入 ThemeManager** (收益最大)
5. **替换渐变标题栏** (消除大量重复代码)

### 逐步迁移策略

**第一阶段**: 工具函数迁移
- ✅ 剪贴板工具
- ✅ 键盘模拟
- ✅ 窗口管理
- ✅ 数据管理

**第二阶段**: UI组件迁移
- ✅ 主题管理器
- ✅ 渐变标题栏
- ✅ 可点击标签

**第三阶段**: 完全重构
- 将 SettingsDialog 分离到 ui/settings_dialog.py
- 将 ClipboardWindow 分离到 ui/clipboard_window.py
- main.py 仅保留程序入口逻辑

---

## 🎨 示例：完整的主题切换

```python
# 在 ClipboardWindow 中
def apply_theme(self, theme, color_scheme):
    """应用主题"""
    # 更新主题管理器
    self.theme_manager.set_theme(theme)
    self.theme_manager.set_color_scheme(color_scheme)

    # 更新所有组件
    self.header.setDarkMode(self.theme_manager.is_dark)
    self.header.setColorScheme(color_scheme)

    # 更新主容器
    self.main_container.setStyleSheet(self.theme_manager.get_container_style())

    # 更新列表
    self.list_widget.setStyleSheet(self.theme_manager.get_list_widget_style())

    # 重新渲染列表项
    self.update_list()
```

这样，一个函数就能完成所有主题切换！

---

## 🚀 开始重构

建议从最简单的开始：

1. 先测试模块是否能正常导入
2. 逐个替换工具函数
3. 观察是否有任何错误
4. 逐步推进到UI组件

需要我帮您开始重构 main.py 吗？
