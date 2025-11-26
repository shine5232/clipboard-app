"""
多选剪贴板助手 - Windows 桌面版
支持 Ctrl+C 自动添加，批量粘贴（逗号分隔）
"""

import sys
import time
import json
import ctypes

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    try:
        import io
        # 设置 line_buffering=True 确保每行输出都立即刷新
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except:
        pass

from datetime import datetime
from pathlib import Path
from functools import partial
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QListWidgetItem,
                             QMessageBox, QMenu, QAction, QSystemTrayIcon,
                             QDialog, QComboBox, QFormLayout, QFrame)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor

# 导入工具模块
from utils.clipboard_utils import get_clipboard_text, set_clipboard_text, process_clipboard_text
from utils.keyboard_simulator import simulate_paste
from utils.window_manager import get_foreground_window, set_foreground_window
from utils.data_manager import ClipboardDataManager

# 导入主题模块
from themes.theme_manager import ThemeManager, get_color_scheme_colors

# 导入UI组件
from ui.components.clickable_label import ClickableLabel
from ui.components.floating_icon import FloatingIcon
from ui.components.tray_menu import TrayMenu


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings or {'output_mode': 'comma', 'theme': 'light', 'color_scheme': 'pure_blue'}
        self.temp_settings = self.settings.copy()

        # 创建主题管理器
        self.theme_manager = ThemeManager(
            theme=self.settings.get('theme', 'light'),
            color_scheme=self.settings.get('color_scheme', 'pure_blue')
        )

        self.init_ui()

    def init_ui(self):
        """初始化设置界面"""
        self.setWindowTitle('设置')
        self.setFixedSize(380, 300)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 主容器
        main_container = QWidget()
        main_container.setObjectName('settingsContainer')

        # 添加阴影效果
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        main_container.setGraphicsEffect(shadow)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        header = self.create_header()
        main_layout.addWidget(header)

        # 内容区域
        content = QWidget()
        content.setObjectName('settingsContent')
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 15)
        content_layout.setSpacing(20)

        # 输出模式配置
        output_group = self.create_setting_row(
            '输出模式',
            '选择粘贴时的输出方式',
            ['逗号拼接', '顺序输出', '倒序输出'],
            {'comma': 0, 'sequential': 1, 'reverse': 2}.get(self.settings.get('output_mode'), 0),
            'output_mode'
        )
        content_layout.addWidget(output_group)

        # 系统主题配置
        theme_group = self.create_setting_row(
            '系统主题',
            '选择界面显示主题',
            ['日间模式', '暗夜模式'],
            0 if self.settings.get('theme') == 'light' else 1,
            'theme'
        )
        content_layout.addWidget(theme_group)

        # 配色方案配置
        color_scheme_group = self.create_setting_row(
            '配色方案',
            '选择界面的配色风格',
            ['蓝渐变', '纯蓝色', '纯绿色'],
            {'blue_gradient': 0, 'pure_blue': 1, 'pure_green': 2}.get(self.settings.get('color_scheme', 'pure_blue'), 0),
            'color_scheme'
        )
        content_layout.addWidget(color_scheme_group)

        content_layout.addStretch()

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        self.apply_btn = QPushButton('应用')
        self.apply_btn.setObjectName('applyBtn')
        self.apply_btn.setFixedSize(70, 32)
        self.apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_btn)

        self.ok_btn = QPushButton('确定')
        self.ok_btn.setObjectName('okBtn')
        self.ok_btn.setFixedSize(70, 32)
        self.ok_btn.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.setObjectName('cancelBtn')
        self.cancel_btn.setFixedSize(70, 32)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        content_layout.addLayout(button_layout)
        content.setLayout(content_layout)
        main_layout.addWidget(content)

        main_container.setLayout(main_layout)

        # 外层布局
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.addWidget(main_container)
        self.setLayout(outer_layout)

        # 应用样式
        self.apply_style()

    def create_header(self):
        """创建标题栏"""
        from PyQt5.QtGui import QPainter, QPainterPath, QLinearGradient
        from PyQt5.QtCore import QRectF

        class HeaderWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.is_dark = False
                self.color_scheme = 'pure_blue'

            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                rect = QRectF(self.rect())
                radius = 10
                path.moveTo(rect.left(), rect.bottom())
                path.lineTo(rect.left(), rect.top() + radius)
                path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
                path.lineTo(rect.right() - radius, rect.top())
                path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
                path.lineTo(rect.right(), rect.bottom())
                path.lineTo(rect.left(), rect.bottom())
                gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())

                # 获取配色方案的颜色
                color1, color2 = get_color_scheme_colors(self.color_scheme, self.is_dark)
                gradient.setColorAt(0, QColor(color1))
                gradient.setColorAt(1, QColor(color2))
                painter.fillPath(path, gradient)

            def setDarkMode(self, is_dark):
                self.is_dark = is_dark
                self.update()

            def setColorScheme(self, scheme):
                self.color_scheme = scheme
                self.update()

        header = HeaderWidget()
        self.settings_header = header  # 保存引用以便后续更新
        header.setFixedHeight(45)

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 15, 0)

        title = QLabel('设置')
        title.setStyleSheet('color: white; font-size: 15px; font-weight: 600; background: transparent;')
        layout.addWidget(title)
        layout.addStretch()

        close_btn = QPushButton('×')
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet(self.theme_manager.get_header_close_button_style())
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

        header.setLayout(layout)

        # 拖拽支持
        header.mousePressEvent = self.header_mouse_press
        header.mouseMoveEvent = self.header_mouse_move

        return header

    def header_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def header_mouse_move(self, event):
        if hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def create_setting_row(self, title, description, options, current_index, setting_key):
        """创建设置行"""
        from PyQt5.QtWidgets import QStyledItemDelegate, QListView
        from PyQt5.QtCore import QSize

        group = QWidget()
        group.setObjectName('settingGroup')
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # 左侧标签区域
        label_widget = QWidget()
        label_layout = QVBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName('settingTitle')
        label_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName('settingDesc')
        label_layout.addWidget(desc_label)

        label_widget.setLayout(label_layout)
        layout.addWidget(label_widget)
        layout.addStretch()

        # 自定义下拉项委托
        class ComboItemDelegate(QStyledItemDelegate):
            def __init__(self, parent=None):
                super().__init__(parent)

            def sizeHint(self, option, index):
                return QSize(100, 36)

        # 右侧下拉框
        combo = QComboBox()
        combo.setObjectName('settingCombo')
        combo.setFixedSize(120, 34)

        # 设置下拉视图
        list_view = QListView()
        list_view.setItemDelegate(ComboItemDelegate())
        combo.setView(list_view)

        # 设置下拉框最大显示项数
        combo.setMaxVisibleItems(5)

        combo.addItems(options)
        combo.setCurrentIndex(current_index)
        combo.currentIndexChanged.connect(lambda idx: self.on_setting_changed(setting_key, idx))
        layout.addWidget(combo)

        # 保存下拉框引用
        setattr(self, f'{setting_key}_combo', combo)

        group.setLayout(layout)
        return group

    def on_setting_changed(self, key, index):
        """设置项变化时的处理"""
        if key == 'output_mode':
            mode_map = {0: 'comma', 1: 'sequential', 2: 'reverse'}
            self.temp_settings['output_mode'] = mode_map.get(index, 'comma')
        elif key == 'theme':
            self.temp_settings['theme'] = 'light' if index == 0 else 'dark'
        elif key == 'color_scheme':
            scheme_map = {0: 'blue_gradient', 1: 'pure_blue', 2: 'pure_green'}
            self.temp_settings['color_scheme'] = scheme_map.get(index, 'pure_blue')

    def apply_settings(self):
        """应用设置（不关闭对话框）"""
        self.settings.update(self.temp_settings)
        # 更新设置对话框自身的主题样式
        self.apply_style()
        # 更新主窗口的设置
        if self.parent():
            self.parent().apply_settings(self.settings)

    def accept_settings(self):
        """确定并关闭"""
        self.apply_settings()
        self.accept()

    def apply_style(self):
        """应用样式"""
        # 更新主题管理器
        self.theme_manager.set_theme(self.settings.get('theme', 'light'))
        self.theme_manager.set_color_scheme(self.settings.get('color_scheme', 'pure_blue'))

        # 更新标题栏主题和配色方案
        if hasattr(self, 'settings_header'):
            self.settings_header.setDarkMode(self.theme_manager.is_dark)
            self.settings_header.setColorScheme(self.theme_manager.color_scheme)

        self.update_style()

    def update_style(self):
        """更新样式"""
        # 使用主题管理器获取样式
        is_dark = self.theme_manager.is_dark

        # 容器样式
        container_style = f"""
            #settingsContainer {{
                background: {'#1e1e1e' if is_dark else '#ffffff'};
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 10px;
            }}
            #settingsContent {{
                background: {'#1e1e1e' if is_dark else '#ffffff'};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }}
        """

        # 设置标题和描述样式 - 替换 QLabel 为 #settingTitle / #settingDesc
        setting_title_style = self.theme_manager.get_setting_title_style().replace('QLabel', '#settingTitle')
        setting_desc_style = self.theme_manager.get_setting_desc_style().replace('QLabel', '#settingDesc')

        # 按钮样式 - 替换 QPushButton 为具体的 ID 选择器
        primary_btn_style = self.theme_manager.get_primary_button_style().replace('QPushButton', '#applyBtn, #okBtn')
        secondary_btn_style = self.theme_manager.get_secondary_button_style().replace('QPushButton', '#cancelBtn')

        # 组合所有样式
        full_style = (
            container_style +
            setting_title_style +
            setting_desc_style +
            self.theme_manager.get_combo_box_style() +
            primary_btn_style +
            secondary_btn_style
        )

        self.setStyleSheet(full_style)

class ClipboardWindow(QWidget):
    """剪贴板悬浮窗"""

    # 自定义信号
    clipboard_changed_signal = pyqtSignal()
    toggle_window_signal = pyqtSignal()
    quit_app_signal = pyqtSignal()
    do_paste_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        # 数据管理器
        self.data_manager = ClipboardDataManager()

        # 数据存储
        self.clipboard_data = []
        self.data_file = Path(__file__).parent / 'data' / 'clipboard_data.json'
        self.settings_file = Path(__file__).parent / 'data' / 'settings.json'

        # 设置
        self.settings = {'output_mode': 'comma', 'theme': 'light', 'color_scheme': 'pure_blue'}
        self.load_settings()

        # 主题管理器
        self.theme_manager = ThemeManager(
            theme=self.settings.get('theme', 'light'),
            color_scheme=self.settings.get('color_scheme', 'pure_blue')
        )

        # 拖拽相关
        self.dragging = False
        self.drag_position = QPoint()

        # 状态管理
        self.last_pasted_text = ""
        self.last_paste_time = 0  # 最后一次粘贴的时间戳
        self.paste_ignore_until = 0  # 时间戳，在此之前忽略剪贴板变化
        self.sequential_index = -1  # 顺序输出模式的当前索引（从最后一项开始）
        self.previous_window = None  # 记录前一个活动窗口

        # 胶囊模式
        self.is_capsule_mode = False  # 是否处于胶囊模式
        self.floating_icon = None  # 浮动图标组件

        # 初始化UI
        self.init_ui()

        # 加载数据
        self.load_data()

        # 连接信号
        self.clipboard_changed_signal.connect(self.on_clipboard_changed)
        self.toggle_window_signal.connect(self.do_toggle_window)
        self.quit_app_signal.connect(self.do_quit_app)
        self.do_paste_signal.connect(self.do_paste)

        # 注册为剪贴板监听器
        self.register_clipboard_listener()

        # 注册全局快捷键
        self.register_hotkeys()

        # 初始化系统托盘图标
        self.init_tray_icon()

        # 应用保存的主题
        self.apply_theme(self.settings.get('theme', 'light'), self.settings.get('color_scheme', 'pure_blue'))

        # 更新模式标识
        self.update_mode_label()

    def register_clipboard_listener(self):
        """注册 Windows 剪贴板监听器"""
        # 使用定时器轮询剪贴板（最可靠的方式）
        self.last_clipboard_text = get_clipboard_text() or ""
        # 不指定父对象，确保定时器独立于窗口可见性运行
        self.clipboard_check_timer = QTimer()
        self.clipboard_check_timer.timeout.connect(self.check_clipboard_change)
        self.clipboard_check_timer.start(300)  # 每300ms检查一次

    def check_clipboard_change(self):
        """检查剪贴板是否变化"""
        current_time = time.time()

        # 如果在忽略时间内，跳过
        if current_time < self.paste_ignore_until:
            return

        try:
            current_text = get_clipboard_text()
            if current_text and current_text != self.last_clipboard_text:
                # 检查是否是我们刚粘贴的内容（带时间窗口检查）
                if current_text == self.last_pasted_text and current_time < self.last_paste_time + 3.0:
                    self.last_clipboard_text = current_text
                    return

                self.last_clipboard_text = current_text
                self.clipboard_changed_signal.emit()
        except Exception as e:
            print(f"检查剪贴板失败: {e}")

    def on_clipboard_changed(self):
        """处理剪贴板变化"""
        text = self.last_clipboard_text
        if not text:
            return

        try:
            # 处理文本（使用导入的函数）
            texts = process_clipboard_text(text)

            # 添加数据
            added_count = 0
            for text_item in texts:
                if not any(item['text'] == text_item for item in self.clipboard_data):
                    self.clipboard_data.append({
                        'text': text_item,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    added_count += 1

            if added_count > 0:
                self.sequential_index = -1  # 重置顺序输出索引
                self.update_list()
                self.save_data()

                # 只在窗口隐藏时显示通知
                if not self.isVisible():
                    if added_count == 1:
                        self.show_notification(f'已复制: {texts[0][:20]}...' if len(texts[0]) > 20 else f'已复制: {texts[0]}')
                    else:
                        self.show_notification(f'已添加 {added_count} 项')
        except Exception as e:
            print(f"处理剪贴板变化失败: {e}")

    def register_hotkeys(self):
        """注册全局快捷键"""
        try:
            from pynput.keyboard import GlobalHotKeys

            def on_paste_hotkey():
                # 使用信号确保在主线程执行
                self.do_paste_signal.emit()

            def on_toggle_hotkey():
                self.toggle_window_signal.emit()

            def on_quit_hotkey():
                self.quit_app_signal.emit()

            self.hotkey_listener = GlobalHotKeys({
                '<ctrl>+<space>': on_paste_hotkey,
                '<ctrl>+<shift>+c': on_toggle_hotkey,
                '<ctrl>+<shift>+q': on_quit_hotkey
            })
            self.hotkey_listener.start()
        except Exception as e:
            print(f"快捷键注册失败: {e}")

    def do_paste(self):
        """执行批量粘贴：自动粘贴到当前位置"""
        if not self.clipboard_data:
            return

        output_mode = self.settings.get('output_mode', 'comma')

        if output_mode == 'sequential':
            # 顺序输出模式：先进先出（FIFO），从第一项开始
            # 初始化或重置索引（从第一项开始）
            if self.sequential_index < 0 or self.sequential_index >= len(self.clipboard_data):
                self.sequential_index = 0

            current_item = self.clipboard_data[self.sequential_index]
            text_to_paste = current_item['text'] if isinstance(current_item, dict) else current_item

            # 记录粘贴的内容和时间
            self.last_pasted_text = text_to_paste
            self.last_paste_time = time.time()
            self.paste_ignore_until = time.time() + 1.5

            # 设置剪贴板
            if set_clipboard_text(text_to_paste):
                self.last_clipboard_text = text_to_paste
                # 延迟250ms执行粘贴
                QTimer.singleShot(250, lambda: self._execute_paste(mode='sequential'))

        elif output_mode == 'reverse':
            # 倒序输出模式：后入先出（LIFO），从最后一项开始
            # 初始化或重置索引（从最后一项开始）
            if self.sequential_index < 0 or self.sequential_index >= len(self.clipboard_data):
                self.sequential_index = len(self.clipboard_data) - 1

            current_item = self.clipboard_data[self.sequential_index]
            text_to_paste = current_item['text'] if isinstance(current_item, dict) else current_item

            # 记录粘贴的内容和时间
            self.last_pasted_text = text_to_paste
            self.last_paste_time = time.time()
            self.paste_ignore_until = time.time() + 1.5

            # 设置剪贴板
            if set_clipboard_text(text_to_paste):
                self.last_clipboard_text = text_to_paste
                # 延迟250ms执行粘贴
                QTimer.singleShot(250, lambda: self._execute_paste(mode='reverse'))

        else:
            # 逗号拼接模式：拼接所有文本
            texts = [item['text'] if isinstance(item, dict) else item for item in self.clipboard_data]
            combined_text = ','.join(texts)

            # 记录粘贴的内容和时间
            self.last_pasted_text = combined_text
            self.last_paste_time = time.time()
            self.paste_ignore_until = time.time() + 1.5

            # 设置剪贴板
            if set_clipboard_text(combined_text):
                self.last_clipboard_text = combined_text
                # 延迟250ms执行粘贴
                QTimer.singleShot(250, lambda: self._execute_paste(mode='comma'))

    def _execute_paste(self, mode='comma'):
        """执行实际的粘贴操作"""
        # 模拟粘贴
        simulate_paste()

        # 根据模式移动索引
        if mode == 'sequential':
            # 顺序输出：向后移动
            self.sequential_index += 1
            # 如果到达末尾，循环回到开头
            if self.sequential_index >= len(self.clipboard_data):
                self.sequential_index = 0
        elif mode == 'reverse':
            # 倒序输出：向前移动
            self.sequential_index -= 1
            # 如果到达开头，循环回到最后
            if self.sequential_index < 0:
                self.sequential_index = len(self.clipboard_data) - 1

    def show_notification(self, message):
        """显示系统通知"""
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.showMessage('剪贴板助手', message, QSystemTrayIcon.Information, 1500)

    # ==================== UI 相关方法（保持不变）====================

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('剪贴板')
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.setFixedSize(360, 560)
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width() - 380, screen.height() - 600)

        self.main_container = QWidget()
        # 使用主题管理器设置容器样式
        self.main_container.setStyleSheet(self.theme_manager.get_container_style())

        container_shadow = self.create_shadow()
        self.main_container.setGraphicsEffect(container_shadow)

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        header = self.create_header()
        container_layout.addWidget(header)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(4)
        # 使用主题管理器设置列表样式
        self.list_widget.setStyleSheet(self.theme_manager.get_list_widget_style())
        container_layout.addWidget(self.list_widget)

        self.main_container.setLayout(container_layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_container)
        self.setLayout(outer_layout)

    def create_header(self):
        """创建头部"""
        from PyQt5.QtGui import QPainter, QPainterPath, QLinearGradient

        parent_window = self

        class HeaderWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.is_dark = False
                self.color_scheme = 'pure_blue'

            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                from PyQt5.QtCore import QRectF

                path = QPainterPath()
                rect = QRectF(self.rect())

                radius = 10
                path.moveTo(rect.left(), rect.bottom())
                path.lineTo(rect.left(), rect.top() + radius)
                path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
                path.lineTo(rect.right() - radius, rect.top())
                path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
                path.lineTo(rect.right(), rect.bottom())
                path.lineTo(rect.left(), rect.bottom())

                gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())

                # 获取配色方案的颜色
                color1, color2 = get_color_scheme_colors(self.color_scheme, self.is_dark)
                gradient.setColorAt(0, QColor(color1))
                gradient.setColorAt(1, QColor(color2))
                painter.fillPath(path, gradient)

            def setDarkMode(self, is_dark):
                self.is_dark = is_dark
                self.update()

            def setColorScheme(self, scheme):
                self.color_scheme = scheme
                self.update()

        header = HeaderWidget()
        header.setFixedHeight(50)
        header.setStyleSheet(self.theme_manager.get_header_button_style() + self.theme_manager.get_header_label_style())

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 0, 12, 0)

        self.title_label = QLabel('剪贴板 (0)')
        layout.addWidget(self.title_label)
        layout.addStretch()

        # 输出模式标识
        self.mode_label = QLabel('拼')
        self.mode_label.setFixedSize(20, 20)
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet(self.theme_manager.get_header_mode_label_style())
        self.mode_label.setToolTip('当前输出模式')
        layout.addWidget(self.mode_label)

        clear_btn = QPushButton()
        clear_btn.setFixedSize(20, 20)
        clear_btn.clicked.connect(self.clear_clipboard)
        clear_btn.setToolTip('清空剪贴板')

        from PyQt5.QtGui import QPixmap, QPen

        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.white, 1.5)
        painter.setPen(pen)
        painter.drawLine(5, 6, 15, 6)
        painter.drawLine(7, 4, 13, 4)
        painter.drawRect(6, 7, 8, 9)
        painter.drawLine(8, 9, 8, 14)
        painter.drawLine(10, 9, 10, 14)
        painter.drawLine(12, 9, 12, 14)
        painter.end()

        clear_btn.setIcon(QIcon(pixmap))
        clear_btn.setStyleSheet(self.theme_manager.get_header_clear_button_style())
        layout.addWidget(clear_btn)

        # 设置按钮（齿轮图标）
        settings_btn = QPushButton()
        settings_btn.setFixedSize(20, 20)
        settings_btn.setToolTip('设置')

        # 绘制齿轮图标
        from PyQt5.QtGui import QPixmap, QPen
        gear_pixmap = QPixmap(20, 20)
        gear_pixmap.fill(Qt.transparent)
        gear_painter = QPainter(gear_pixmap)
        gear_painter.setRenderHint(QPainter.Antialiasing)
        gear_pen = QPen(Qt.white, 1.5)
        gear_painter.setPen(gear_pen)
        gear_painter.setBrush(Qt.NoBrush)
        # 外圆（齿轮主体）
        gear_painter.drawEllipse(5, 5, 10, 10)
        # 内圆
        gear_painter.drawEllipse(7, 7, 6, 6)
        # 齿轮齿（8个方向的短线）
        import math
        center_x, center_y = 10, 10
        for i in range(8):
            angle = i * math.pi / 4
            x1 = center_x + 5 * math.cos(angle)
            y1 = center_y + 5 * math.sin(angle)
            x2 = center_x + 8 * math.cos(angle)
            y2 = center_y + 8 * math.sin(angle)
            gear_painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        gear_painter.end()

        settings_btn.setIcon(QIcon(gear_pixmap))
        settings_btn.setStyleSheet(self.theme_manager.get_header_icon_button_style())
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)

        close_btn = QPushButton('×')
        close_btn.setFixedSize(20, 20)
        close_btn.setToolTip('隐藏窗口')
        close_btn.setStyleSheet(self.theme_manager.get_header_close_button_style())
        close_btn.clicked.connect(self.hide_window)
        layout.addWidget(close_btn)

        header.setLayout(layout)
        header.mousePressEvent = self.header_mouse_press
        header.mouseMoveEvent = self.header_mouse_move
        header.mouseReleaseEvent = self.header_mouse_release
        header.mouseDoubleClickEvent = self.header_double_click

        self.header = header
        return header

    def header_double_click(self, event):
        """双击标题栏切换胶囊模式"""
        if event.button() == Qt.LeftButton:
            self.toggle_capsule_mode()
            event.accept()

    def create_shadow(self):
        """创建阴影效果"""
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        return shadow

    def init_tray_icon(self):
        """初始化系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)

        from PyQt5.QtGui import QPixmap, QPainter
        from PyQt5.QtCore import QRect

        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor('#667eea'))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        painter.setPen(QColor('white'))
        font = QFont('Arial', 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, 64, 64), Qt.AlignCenter, 'CB')
        painter.end()

        self.tray_icon.setIcon(QIcon(pixmap))

        # 创建自定义托盘菜单
        self.tray_menu = TrayMenu()
        self.tray_menu.show_window_clicked.connect(self.show_window)
        self.tray_menu.quit_clicked.connect(self.do_quit_app)

        # 设置主题
        is_dark = self.settings.get('theme') == 'dark'
        color_scheme = self.settings.get('color_scheme', 'pure_blue')
        self.tray_menu.set_theme(is_dark, color_scheme)

        # 不使用系统默认菜单，改用自定义菜单
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        self.tray_icon.setToolTip('剪贴板助手\nCtrl+Shift+C: 显示/隐藏\nCtrl+Space: 批量粘贴\nCtrl+Shift+Q: 退出')

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.do_toggle_window()
        elif reason == QSystemTrayIcon.Context:
            # 右键点击显示自定义菜单
            self.tray_menu.show_at_cursor()

    def header_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def header_mouse_move(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def header_mouse_release(self, event):
        self.dragging = False

    def update_mode_label(self):
        """更新输出模式标识"""
        output_mode = self.settings.get('output_mode', 'comma')
        mode_text = {
            'comma': '拼',
            'sequential': '顺',
            'reverse': '倒'
        }.get(output_mode, '拼')

        mode_tooltip = {
            'comma': '逗号拼接',
            'sequential': '顺序输出',
            'reverse': '倒序输出'
        }.get(output_mode, '逗号拼接')

        if hasattr(self, 'mode_label'):
            self.mode_label.setText(mode_text)
            self.mode_label.setToolTip(f'当前输出模式：{mode_tooltip}')

    def update_list(self):
        """更新列表显示"""
        self.list_widget.clear()
        self.title_label.setText(f'剪贴板 ({len(self.clipboard_data)})')

        # 更新胶囊数量
        self.update_capsule_count()

        is_dark = self.settings.get('theme') == 'dark'

        if not self.clipboard_data:
            item = QListWidgetItem('暂无数据')
            item.setFlags(Qt.NoItemFlags)
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor('#888888' if is_dark else '#909399'))
            item.setBackground(QBrush(QColor(255, 255, 255, 0)))
            self.list_widget.addItem(item)
            return

        for i, data in enumerate(self.clipboard_data):
            item_widget = self.create_list_item(i, data)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

    def create_list_item(self, index, data):
        """创建列表项"""
        if isinstance(data, str):
            text = data
            timestamp = datetime.now().strftime('%H:%M:%S')
        else:
            text = data['text']
            timestamp = data.get('timestamp', datetime.now().strftime('%H:%M:%S'))

        widget = QWidget()
        widget.setMinimumHeight(40)

        # 使用主题管理器设置样式
        widget.setStyleSheet(self.theme_manager.get_list_item_style())

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # 使用导入的 ClickableLabel 组件
        label = ClickableLabel(
            text=text,
            callback=self.paste_single_item,
            data=text
        )
        label.setWordWrap(False)
        label.setFixedWidth(200)
        label.setToolTip(text)

        # 使用主题管理器设置标签样式
        label.setStyleSheet(self.theme_manager.get_label_style(font_size=13))

        label.setTextFormat(Qt.PlainText)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font_metrics = label.fontMetrics()
        elided_text = font_metrics.elidedText(text, Qt.ElideRight, 200)
        label.setText(elided_text)

        layout.addWidget(label)
        layout.addStretch()

        time_label = QLabel(timestamp)
        # 使用主题管理器设置时间标签样式
        time_label.setStyleSheet(self.theme_manager.get_time_label_style())
        time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(time_label)

        delete_btn = QPushButton('×')
        delete_btn.setFixedSize(20, 20)
        # 使用主题管理器设置删除按钮样式
        delete_btn.setStyleSheet(self.theme_manager.get_delete_button_style())
        delete_btn.clicked.connect(partial(self.remove_item_by_text, text))
        layout.addWidget(delete_btn)

        widget.setLayout(layout)

        return widget

    def paste_single_item(self, text):
        """粘贴单个项目到光标位置"""
        if not text:
            return

        try:
            # 记录粘贴的内容和时间
            self.last_pasted_text = text
            self.last_paste_time = time.time()
            self.paste_ignore_until = time.time() + 1.5

            # 设置剪贴板
            if set_clipboard_text(text):
                self.last_clipboard_text = text

                # 隐藏窗口
                self.hide()

                # 激活前一个窗口
                if self.previous_window:
                    set_foreground_window(self.previous_window)
                    time.sleep(0.1)  # 给窗口激活留出时间

                # 延迟400ms执行粘贴
                QTimer.singleShot(400, self._execute_single_paste)
        except Exception as e:
            print(f"单项粘贴失败: {e}")

    def _execute_single_paste(self):
        """执行单项粘贴操作"""
        simulate_paste()

    def remove_item_by_text(self, text):
        """删除指定项"""
        # 使用列表推导式创建新列表，避免遍历中删除的问题
        original_length = len(self.clipboard_data)
        self.clipboard_data = [
            item for item in self.clipboard_data
            if (item['text'] if isinstance(item, dict) else item) != text
        ]

        # 如果列表长度发生变化，说明删除成功
        if len(self.clipboard_data) < original_length:
            self.update_list()
            self.save_data()

    def clear_clipboard(self):
        """清空剪贴板"""
        if not self.clipboard_data:
            return

        reply = QMessageBox.question(
            self, '确认', '确定要清空所有剪贴板数据吗？',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.clipboard_data.clear()
            self.sequential_index = -1  # 重置顺序输出索引
            self.update_list()
            self.save_data()
            set_clipboard_text('')
            self.last_clipboard_text = ''

    def hide_window(self):
        self.hide()

    def show_window(self):
        """显示主窗口"""
        # 如果处于胶囊模式，先退出胶囊模式
        if self.is_capsule_mode:
            self.restore_from_capsule()
            return

        # 记录当前活动窗口（在显示剪贴板窗口之前）
        self.previous_window = get_foreground_window()

        self.show()
        self.activateWindow()
        self.raise_()

    def do_toggle_window(self):
        """切换窗口显示状态"""
        # 如果处于胶囊模式，恢复主窗口
        if self.is_capsule_mode:
            self.restore_from_capsule()
        elif self.isVisible():
            self.hide_window()
        else:
            self.show_window()

    def save_data(self):
        """保存数据"""
        try:
            self.data_file.parent.mkdir(exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.clipboard_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def load_data(self):
        """加载数据"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.clipboard_data = []
                    for item in loaded_data:
                        if isinstance(item, str):
                            self.clipboard_data.append({
                                'text': item,
                                'timestamp': datetime.now().strftime('%H:%M:%S')
                            })
                        else:
                            self.clipboard_data.append(item)
                    self.update_list()
        except Exception as e:
            print(f"加载数据失败: {e}")

    def save_settings(self):
        """保存设置"""
        try:
            self.settings_file.parent.mkdir(exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")

    def load_settings(self):
        """加载设置"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            else:
                # 首次启动，检测系统主题
                self.settings['theme'] = self.detect_system_theme()
        except Exception as e:
            print(f"加载设置失败: {e}")
            # 出错时也尝试检测系统主题
            self.settings['theme'] = self.detect_system_theme()

    def detect_system_theme(self):
        """检测 Windows 系统主题"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return 'light' if value == 1 else 'dark'
        except Exception:
            return 'light'  # 默认日间模式

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self, self.settings.copy())
        dialog.exec_()

    def init_capsule_widget(self):
        """初始化浮动图标"""
        if self.floating_icon is None:
            self.floating_icon = FloatingIcon()
            # 设置主题
            is_dark = self.settings.get('theme') == 'dark'
            color_scheme = self.settings.get('color_scheme', 'pure_blue')
            self.floating_icon.set_theme(is_dark, color_scheme)
            # 连接信号
            self.floating_icon.double_clicked.connect(self.restore_from_capsule)

        # 每次进入胶囊模式都同步最新数量
        self.floating_icon.count = len(self.clipboard_data)

    def toggle_capsule_mode(self):
        """切换胶囊模式"""
        if self.is_capsule_mode:
            # 从胶囊模式恢复
            self.restore_from_capsule()
        else:
            # 进入胶囊模式
            self.enter_capsule_mode()

    def enter_capsule_mode(self):
        """进入胶囊模式"""
        if self.is_capsule_mode:
            return

        self.is_capsule_mode = True

        # 初始化浮动图标
        self.init_capsule_widget()

        # 获取主窗口标题栏位置作为动画起点
        start_pos = self.pos()
        # 标题栏中心位置（标题栏高度约50px）
        start_x = start_pos.x() + self.width() // 2
        start_y = start_pos.y() + 25  # 标题栏中心位置

        # 隐藏主窗口
        self.hide()

        # 计算目标位置（屏幕右侧胶囊位置）
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QRect, QPropertyAnimation, QEasingCurve, QTimer
        screen = QApplication.desktop().screenGeometry()

        capsule_x = screen.width() - self.floating_icon.capsule_width
        capsule_y = (screen.height() - self.floating_icon.capsule_height) // 2

        # 先设置为小圆形（使用较小的尺寸），从标题栏位置开始
        small_size = 40  # 小圆形大小
        self.floating_icon.is_capsule_mode = False
        self.floating_icon.setGeometry(start_x - small_size // 2,
                                       start_y - small_size // 2,
                                       small_size,
                                       small_size)
        self.floating_icon.show()

        # 第一阶段：小圆形飞到右侧并放大到正常圆形大小
        fly_animation = QPropertyAnimation(self.floating_icon, b"geometry")
        fly_animation.setDuration(600)  # 600ms飞行动画
        fly_animation.setEasingCurve(QEasingCurve.OutCubic)

        # 飞行目标：屏幕右侧边缘位置（贴边），放大到正常圆形大小
        # 让圆形直接飞到右边缘，圆形的右边缘贴着屏幕边缘
        fly_target_x = screen.width() - self.floating_icon.icon_size
        fly_target_y = (screen.height() - self.floating_icon.icon_size) // 2

        fly_animation.setStartValue(QRect(start_x - small_size // 2,
                                          start_y - small_size // 2,
                                          small_size,
                                          small_size))
        fly_animation.setEndValue(QRect(fly_target_x, fly_target_y,
                                        self.floating_icon.icon_size,
                                        self.floating_icon.icon_size))

        # 飞行完成后，延迟变形为胶囊
        def on_fly_finished():
            # 300ms后变形为胶囊
            QTimer.singleShot(300, lambda: self.floating_icon.morph_to_capsule() if self.floating_icon else None)

        fly_animation.finished.connect(on_fly_finished)
        fly_animation.start()

        # 保存动画引用，避免被垃圾回收
        self.floating_icon._fly_animation = fly_animation

    def restore_from_capsule(self):
        """从胶囊模式恢复"""
        if not self.is_capsule_mode:
            return

        self.is_capsule_mode = False

        # 获取浮动图标当前位置，将主窗口移动到该位置附近
        if self.floating_icon:
            icon_pos = self.floating_icon.pos()
            # 计算主窗口位置：让主窗口的右上角对齐图标位置
            # 向左偏移主窗口宽度，向上稍微偏移
            new_x = icon_pos.x() - self.width() + self.floating_icon.width()
            new_y = icon_pos.y() - 50  # 向上偏移50px，避免被图标遮挡

            # 确保窗口不超出屏幕边界
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.desktop().screenGeometry()

            # 限制在屏幕范围内
            new_x = max(0, min(new_x, screen.width() - self.width()))
            new_y = max(0, min(new_y, screen.height() - self.height()))

            self.move(new_x, new_y)

            # 隐藏浮动图标
            self.floating_icon.hide()

        # 显示主窗口
        self.show()
        self.activateWindow()
        self.raise_()

    def update_capsule_count(self):
        """更新浮动图标显示的数量"""
        if self.floating_icon and self.floating_icon.isVisible():
            self.floating_icon.set_count(len(self.clipboard_data))


    def apply_settings(self, new_settings):
        """应用设置"""
        old_theme = self.settings.get('theme')
        old_output_mode = self.settings.get('output_mode')
        old_color_scheme = self.settings.get('color_scheme')
        self.settings.update(new_settings)
        self.save_settings()

        # 如果输出模式改变，重置索引到起始位置
        if new_settings.get('output_mode') != old_output_mode:
            self.sequential_index = -1  # 重置索引，下次使用时会初始化到正确位置
            self.update_mode_label()  # 更新模式标识

        # 如果主题或配色方案改变，应用新样式
        if new_settings.get('theme') != old_theme or new_settings.get('color_scheme') != old_color_scheme:
            self.apply_theme(new_settings.get('theme'), new_settings.get('color_scheme', 'pure_blue'))

    def apply_theme(self, theme, color_scheme='pure_blue'):
        """应用主题"""
        is_dark = theme == 'dark'
        self.update_theme_style(is_dark, color_scheme)
        self.update_list()  # 重新渲染列表以应用新主题

        # 更新浮动图标主题
        if self.floating_icon:
            self.floating_icon.set_theme(is_dark, color_scheme)

        # 更新托盘菜单主题
        if hasattr(self, 'tray_menu'):
            self.tray_menu.set_theme(is_dark, color_scheme)

    def update_theme_style(self, is_dark=False, color_scheme='pure_blue'):
        """更新主题样式"""
        # 更新主题管理器
        self.theme_manager.set_theme('dark' if is_dark else 'light')
        self.theme_manager.set_color_scheme(color_scheme)

        # 更新标题栏主题和配色方案
        if hasattr(self, 'header'):
            self.header.setDarkMode(is_dark)
            self.header.setColorScheme(color_scheme)

        # 使用主题管理器更新样式
        self.main_container.setStyleSheet(self.theme_manager.get_container_style())
        self.list_widget.setStyleSheet(self.theme_manager.get_list_widget_style())

    def closeEvent(self, event):
        self.save_data()
        event.ignore()
        self.hide()

    def do_quit_app(self):
        """退出程序"""
        # 清除剪贴板数据文件
        self.clear_data_file()

        if hasattr(self, 'clipboard_check_timer'):
            self.clipboard_check_timer.stop()

        if hasattr(self, 'hotkey_listener'):
            try:
                self.hotkey_listener.stop()
            except Exception as e:
                print(f"停止快捷键监听器失败: {e}")

        QApplication.quit()

    def clear_data_file(self):
        """清除剪贴板数据文件"""
        try:
            if self.data_file.exists():
                self.data_file.unlink()
        except Exception as e:
            print(f"清除数据文件失败: {e}")


def check_single_instance():
    """检查是否已有实例运行（Windows平台）"""
    if sys.platform != 'win32':
        return True

    try:
        # 使用Windows互斥量确保只有一个实例运行
        # CreateMutexW: 创建或打开一个命名互斥量
        kernel32 = ctypes.windll.kernel32
        mutex_name = "Global\\ClipboardHelperMutex_UniqueID_20231124"

        # 创建互斥量
        mutex = kernel32.CreateMutexW(None, False, mutex_name)
        last_error = kernel32.GetLastError()

        # ERROR_ALREADY_EXISTS = 183 表示互斥量已存在（程序已在运行）
        if last_error == 183:
            # 显示提示消息
            MessageBox = ctypes.windll.user32.MessageBoxW
            MessageBox(None,
                      "剪贴板助手已经在运行中！\n\n请在系统托盘查看图标，或使用快捷键 Ctrl+Shift+C 显示窗口。",
                      "提示",
                      0x40 | 0x0)  # MB_ICONINFORMATION | MB_OK
            return False

        return True
    except Exception as e:
        print(f"单实例检测失败: {e}")
        return True  # 出错时允许启动


def main():
    # 检查是否已有实例在运行
    if not check_single_instance():
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName('剪贴板助手')

    window = ClipboardWindow()
    window.show()

    if hasattr(window, 'tray_icon') and window.tray_icon:
        window.tray_icon.showMessage(
            '剪贴板助手已启动',
            'Ctrl+Shift+C: 显示/隐藏\nCtrl+Space: 批量粘贴\nCtrl+Shift+Q: 退出',
            QSystemTrayIcon.Information,
            3000
        )

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
