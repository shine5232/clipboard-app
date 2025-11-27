"""
多选剪贴板助手 - Windows 桌面版
支持 Ctrl+C 自动添加，批量粘贴（逗号分隔）
"""

import sys
import time
import json
import ctypes

from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QListWidgetItem,
                             QMessageBox, QMenu, QAction, QSystemTrayIcon,
                             QDialog, QComboBox, QFormLayout, QFrame, QAbstractItemView)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer, QRect
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor, QCursor

# 导入工具模块
from utils.clipboard_utils import get_clipboard_text
from utils.clipboard_listener import ClipboardListener

# 导入业务逻辑层
from services.clipboard_service import ClipboardService

# 导入数据模型层
from models.data_model import DataModel

# 导入主题模块
from themes.theme_manager import ThemeManager, get_color_scheme_colors

# 导入UI组件
from ui.components.floating_icon import FloatingIcon
from ui.components.tray_menu import TrayMenu
from ui.components.clipboard_delegate import ClipboardItemDelegate


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
            ['魅力蓝', '天空蓝', '青草绿', '樱花粉'],
            {'blue_gradient': 0, 'pure_blue': 1, 'pure_green': 2, 'sakura_pink': 3}.get(self.settings.get('color_scheme', 'pure_blue'), 1),
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
            scheme_map = {0: 'blue_gradient', 1: 'pure_blue', 2: 'pure_green', 3: 'sakura_pink'}
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

        # 按钮样式 - 使用参数化选择器
        primary_btn_style = self.theme_manager.get_primary_button_style('#applyBtn, #okBtn')
        secondary_btn_style = self.theme_manager.get_secondary_button_style('#cancelBtn')

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

        # 初始化数据模型层
        self.data_model = DataModel()

        # 初始化业务逻辑层
        self.clipboard_service = ClipboardService()

        # 设置
        self.settings = self.data_model.load_settings()

        # 同步业务层设置
        self.clipboard_service.set_output_mode(self.settings.get('output_mode', 'comma'))

        # 主题管理器
        self.theme_manager = ThemeManager(
            theme=self.settings.get('theme', 'light'),
            color_scheme=self.settings.get('color_scheme', 'pure_blue')
        )

        # 拖拽相关
        self.dragging = False
        self.drag_position = QPoint()

        # 胶囊模式
        self.is_capsule_mode = False  # 是否处于胶囊模式
        self.floating_icon = None  # 浮动图标组件
        self.saved_window_pos = None  # 保存主窗口位置（用于从胶囊模式恢复）
        self.saved_window_pixmap = None  # 保存主窗口截图（用于飞入动画）

        # 初始化UI
        self.init_ui()

        # 加载数据
        self.load_data()

        # 连接业务层信号
        self.clipboard_service.data_changed.connect(self.on_service_data_changed)
        self.clipboard_service.notification_requested.connect(self.show_notification)

        # 连接UI信号
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
        self.clipboard_service.last_clipboard_text = get_clipboard_text() or ""

        # 使用 Windows API 监听剪贴板变化
        self.clipboard_listener = ClipboardListener()
        self.clipboard_listener.clipboard_changed.connect(self.on_clipboard_update)

        if self.clipboard_listener.start():
            pass  # 剪贴板监听器已启动（使用 Windows API）
        else:
            # 如果 API 监听失败，回退到轮询方式
            self.clipboard_check_timer = QTimer()
            self.clipboard_check_timer.timeout.connect(self.check_clipboard_change)
            self.clipboard_check_timer.start(300)

    def on_clipboard_update(self):
        """Windows API 触发的剪贴板更新事件"""
        current_time = time.time()

        # 如果在忽略时间内，跳过
        if current_time < self.clipboard_service.paste_ignore_until:
            return

        try:
            # 延迟一小段时间再读取，确保剪贴板数据已就绪
            QTimer.singleShot(50, self._process_clipboard_update)
        except Exception:
            pass  # 处理剪贴板更新失败

    def _process_clipboard_update(self):
        """处理剪贴板更新"""
        try:
            current_text = get_clipboard_text()
            if current_text:
                # 检查是否与上次相同
                if current_text != self.clipboard_service.last_clipboard_text:
                    if not self.clipboard_service.should_ignore_clipboard_change(current_text):
                        self.clipboard_service.last_clipboard_text = current_text
                        self.clipboard_changed_signal.emit()
                    else:
                        self.clipboard_service.last_clipboard_text = current_text
        except Exception:
            pass  # 读取剪贴板失败

    def check_clipboard_change(self):
        """检查剪贴板是否变化（轮询方式备用）"""
        current_time = time.time()

        # 如果在忽略时间内，跳过
        if current_time < self.clipboard_service.paste_ignore_until:
            return

        try:
            current_text = get_clipboard_text()
            if current_text:
                # 检查是否与上次相同
                if current_text != self.clipboard_service.last_clipboard_text:
                    if not self.clipboard_service.should_ignore_clipboard_change(current_text):
                        self.clipboard_service.last_clipboard_text = current_text
                        self.clipboard_changed_signal.emit()
                    else:
                        self.clipboard_service.last_clipboard_text = current_text
        except Exception:
            pass  # 检查剪贴板失败

    def on_clipboard_changed(self):
        """处理剪贴板变化"""
        text = self.clipboard_service.last_clipboard_text
        if not text:
            return

        try:
            # 使用服务层处理剪贴板变化
            added_count = self.clipboard_service.handle_clipboard_change(
                text,
                is_window_visible=self.isVisible()
            )

            if added_count > 0:
                self.save_data()
        except Exception:
            pass  # 处理剪贴板变化失败

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
        except Exception:
            pass  # 快捷键注册失败

    def do_paste(self):
        """执行批量粘贴：自动粘贴到当前位置"""
        # 使用服务层准备粘贴内容
        text_to_paste, success = self.clipboard_service.prepare_paste_content()

        if success and text_to_paste:
            # 延迟250ms执行粘贴
            QTimer.singleShot(250, self._execute_paste)

    def _execute_paste(self):
        """执行实际的粘贴操作"""
        # 执行粘贴
        self.clipboard_service.execute_paste()

        # 更新索引
        self.clipboard_service.update_sequential_index()

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

        # 设置虚拟化列表委托
        self.item_delegate = ClipboardItemDelegate(self.list_widget, self.theme_manager)
        self.item_delegate.set_theme(self.theme_manager.is_dark)
        self.item_delegate.on_item_click = self.paste_single_item
        self.item_delegate.on_delete_click = self.remove_item_by_text
        self.list_widget.setItemDelegate(self.item_delegate)

        # 启用鼠标追踪以支持悬停效果
        self.list_widget.setMouseTracking(True)
        self.list_widget.viewport().setMouseTracking(True)
        self.list_widget.viewport().installEventFilter(self)

        # 设置统一项目高度以优化性能
        self.list_widget.setUniformItemSizes(True)

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
        close_btn.setToolTip('切换胶囊模式')
        close_btn.setStyleSheet(self.theme_manager.get_header_close_button_style())
        close_btn.clicked.connect(self.toggle_capsule_mode)
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

    def on_service_data_changed(self):
        """业务层数据变化时的回调"""
        self.update_list()

    def update_list(self):
        """更新列表显示 - 使用虚拟化渲染"""
        self.list_widget.clear()

        # 从服务层获取数据
        clipboard_data = self.clipboard_service.get_all_data()
        self.title_label.setText(f'剪贴板 ({len(clipboard_data)})')

        # 更新胶囊数量
        self.update_capsule_count()

        is_dark = self.settings.get('theme') == 'dark'

        # 更新委托主题
        if hasattr(self, 'item_delegate'):
            self.item_delegate.set_theme(is_dark)

        if not clipboard_data:
            item = QListWidgetItem('暂无数据')
            item.setFlags(Qt.NoItemFlags)
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor('#888888' if is_dark else '#909399'))
            item.setBackground(QBrush(QColor(255, 255, 255, 0)))
            self.list_widget.addItem(item)
            return

        # 使用委托渲染，不创建实际的小部件
        for i, data in enumerate(clipboard_data):
            if isinstance(data, str):
                item_data = {
                    'text': data,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            else:
                item_data = {
                    'text': data['text'],
                    'timestamp': data.get('timestamp', datetime.now().strftime('%H:%M:%S'))
                }

            item = QListWidgetItem()
            item.setData(Qt.UserRole, item_data)
            item.setData(Qt.ToolTipRole, item_data['text'])  # 设置提示文本
            item.setSizeHint(self.item_delegate.sizeHint(None, None))
            self.list_widget.addItem(item)

    def eventFilter(self, obj, event):
        """事件过滤器 - 处理列表项悬停效果"""
        from PyQt5.QtCore import QEvent

        if obj == self.list_widget.viewport():
            if event.type() == QEvent.MouseMove:
                # 获取鼠标位置对应的索引
                pos = event.pos()
                index = self.list_widget.indexAt(pos)

                if index.isValid():
                    row = index.row()

                    # 检查是否在删除按钮区域
                    item = self.list_widget.item(row)
                    if item:
                        rect = self.list_widget.visualItemRect(item)
                        # 计算删除按钮区域
                        btn_size = 20
                        margin = 12
                        btn_x = rect.right() - margin - btn_size - 4  # 4是ITEM_MARGIN
                        btn_y = rect.y() + (rect.height() - btn_size) // 2
                        btn_rect = QRect(btn_x, btn_y, btn_size, btn_size)

                        if btn_rect.contains(pos):
                            self.item_delegate.set_hovered_delete_index(row)
                            self.setCursor(Qt.PointingHandCursor)
                        else:
                            self.item_delegate.set_hovered_delete_index(-1)
                            self.setCursor(Qt.PointingHandCursor)

                    # 更新悬停索引
                    if self.item_delegate.hovered_index != row:
                        self.item_delegate.set_hovered_index(row)
                        self.list_widget.viewport().update()
                else:
                    # 鼠标不在任何项上
                    if self.item_delegate.hovered_index != -1:
                        self.item_delegate.set_hovered_index(-1)
                        self.item_delegate.set_hovered_delete_index(-1)
                        self.list_widget.viewport().update()
                        self.setCursor(Qt.ArrowCursor)

            elif event.type() == QEvent.Leave:
                # 鼠标离开列表区域
                if self.item_delegate.hovered_index != -1:
                    self.item_delegate.set_hovered_index(-1)
                    self.item_delegate.set_hovered_delete_index(-1)
                    self.list_widget.viewport().update()
                    self.setCursor(Qt.ArrowCursor)

        return super().eventFilter(obj, event)

    def paste_single_item(self, text):
        """粘贴单个项目到光标位置"""
        if not text:
            return

        try:
            # 使用服务层准备粘贴
            if self.clipboard_service.prepare_single_paste(text):
                # 隐藏窗口
                self.hide()

                # 激活前一个窗口
                self.clipboard_service.restore_previous_window()

                # 延迟400ms执行粘贴
                QTimer.singleShot(400, self._execute_single_paste)
        except Exception:
            pass  # 单项粘贴失败

    def _execute_single_paste(self):
        """执行单项粘贴操作"""
        self.clipboard_service.execute_paste()

    def remove_item_by_text(self, text):
        """删除指定项"""
        if self.clipboard_service.remove_item_by_text(text):
            self.save_data()

    def clear_clipboard(self):
        """清空剪贴板"""
        if self.clipboard_service.get_data_count() == 0:
            return

        reply = QMessageBox.question(
            self, '确认', '确定要清空所有剪贴板数据吗？',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.clipboard_service.clear_all()
            self.save_data()

    def hide_window(self):
        self.hide()

    def show_window(self):
        """显示主窗口"""
        # 如果处于胶囊模式，先退出胶囊模式
        if self.is_capsule_mode:
            self.restore_from_capsule()
            return

        # 记录当前活动窗口（在显示剪贴板窗口之前）
        self.clipboard_service.save_previous_window()

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
        data = self.clipboard_service.get_data_for_save()
        self.data_model.save_clipboard_data(data)

    def load_data(self):
        """加载数据"""
        loaded_data = self.data_model.load_clipboard_data()
        if loaded_data:
            self.clipboard_service.load_data(loaded_data)

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
            # 连接信号：双击和鼠标悬停都恢复主窗口
            self.floating_icon.double_clicked.connect(self.restore_from_capsule)
            self.floating_icon.mouse_entered.connect(self.restore_from_capsule)

        # 每次进入胶囊模式都同步最新数量
        self.floating_icon.count = self.clipboard_service.get_data_count()

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

        # 保存主窗口当前位置（用于恢复）
        self.saved_window_pos = self.pos()

        # 对主窗口进行截图（用于飞出和飞入动画）
        from PyQt5.QtGui import QPixmap
        self.saved_window_pixmap = self.main_container.grab()

        # 初始化浮动图标
        self.init_capsule_widget()

        # 禁用鼠标悬停恢复（防止飞出时立即触发）
        self.floating_icon.allow_hover_restore = False

        # 设置截图到浮动图标
        self.floating_icon.set_window_pixmap(self.saved_window_pixmap)

        # 计算目标位置（屏幕右侧胶囊位置）
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QRect, QPropertyAnimation, QEasingCurve, QTimer
        screen = QApplication.desktop().screenGeometry()

        capsule_x = screen.width() - self.floating_icon.capsule_width
        capsule_y = (screen.height() - self.floating_icon.capsule_height) // 2

        # 胶囊从主窗口的大小和位置开始（显示截图，不是胶囊形状）
        start_x = self.pos().x()
        start_y = self.pos().y()
        start_width = self.width()
        start_height = self.height()

        # 先不设置为胶囊形态，让它显示截图
        self.floating_icon.is_capsule_mode = False
        self.floating_icon.setGeometry(start_x, start_y, start_width, start_height)
        self.floating_icon.show()

        # 延迟隐藏主窗口，让浮动图标先显示出来
        QTimer.singleShot(50, self.hide)

        # 创建缩放飞出动画（从主窗口大小缩小到胶囊大小并移动到右侧）
        fly_animation = QPropertyAnimation(self.floating_icon, b"geometry")
        fly_animation.setDuration(500)  # 500ms缩放飞行动画
        fly_animation.setEasingCurve(QEasingCurve.InOutCubic)

        fly_animation.setStartValue(QRect(start_x, start_y, start_width, start_height))
        fly_animation.setEndValue(QRect(capsule_x, capsule_y,
                                       self.floating_icon.capsule_width,
                                       self.floating_icon.capsule_height))

        # 在动画80%完成时清除截图并切换为胶囊模式
        def switch_to_capsule():
            if self.floating_icon:
                self.floating_icon.clear_window_pixmap()
                self.floating_icon.is_capsule_mode = True
                self.floating_icon.update()

        QTimer.singleShot(400, switch_to_capsule)  # 500ms * 0.8 = 400ms

        # 动画完成后启用鼠标悬停恢复
        def on_fly_finished():
            if self.floating_icon:
                self.floating_icon.allow_hover_restore = True

        fly_animation.finished.connect(on_fly_finished)
        fly_animation.start()

        # 保存动画引用，避免被垃圾回收
        self.floating_icon._fly_animation = fly_animation

    def restore_from_capsule(self):
        """从胶囊模式恢复"""
        if not self.is_capsule_mode:
            return

        self.is_capsule_mode = False

        # 禁用鼠标悬停恢复（防止恢复过程中重复触发）
        if self.floating_icon:
            self.floating_icon.allow_hover_restore = False

        # 获取浮动图标当前位置和保存的主窗口位置
        if self.floating_icon and self.saved_window_pos and self.saved_window_pixmap:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QRect, QPropertyAnimation, QEasingCurve, QTimer

            # 确保窗口不超出屏幕边界
            screen = QApplication.desktop().screenGeometry()
            if self.saved_window_pos.x() < 0 or self.saved_window_pos.x() + self.width() > screen.width():
                self.saved_window_pos.setX(max(0, min(self.saved_window_pos.x(), screen.width() - self.width())))
            if self.saved_window_pos.y() < 0 or self.saved_window_pos.y() + self.height() > screen.height():
                self.saved_window_pos.setY(max(0, min(self.saved_window_pos.y(), screen.height() - self.height())))

            # 创建放大飞入动画（从胶囊大小放大到主窗口大小并移动回原位置）
            fly_back_animation = QPropertyAnimation(self.floating_icon, b"geometry")
            fly_back_animation.setDuration(500)  # 500ms缩放飞行动画
            fly_back_animation.setEasingCurve(QEasingCurve.InOutCubic)

            # 当前位置（胶囊状态）
            current_rect = self.floating_icon.geometry()

            # 目标位置（主窗口大小和位置）
            target_x = self.saved_window_pos.x()
            target_y = self.saved_window_pos.y()
            target_width = self.width()
            target_height = self.height()

            fly_back_animation.setStartValue(current_rect)
            fly_back_animation.setEndValue(QRect(target_x, target_y, target_width, target_height))

            # 在动画20%完成时切换为截图模式
            def switch_to_screenshot():
                if self.floating_icon:
                    self.floating_icon.is_capsule_mode = False
                    self.floating_icon.set_window_pixmap(self.saved_window_pixmap)

            QTimer.singleShot(100, switch_to_screenshot)  # 500ms * 0.2 = 100ms

            # 在动画80%完成时显示主窗口
            def show_main_window():
                self.move(self.saved_window_pos)
                self.show()
                self.activateWindow()
                self.raise_()

            QTimer.singleShot(400, show_main_window)  # 500ms * 0.8 = 400ms

            # 动画完成后隐藏浮动图标并清除截图
            def cleanup():
                if self.floating_icon:
                    self.floating_icon.hide()
                    self.floating_icon.clear_window_pixmap()

            QTimer.singleShot(500, cleanup)

            fly_back_animation.start()

            # 保存动画引用，避免被垃圾回收
            self.floating_icon._fly_back_animation = fly_back_animation
        else:
            # 如果没有保存位置，直接在当前位置显示
            if self.floating_icon:
                self.floating_icon.hide()
            self.show()
            self.activateWindow()
            self.raise_()

    def update_capsule_count(self):
        """更新浮动图标显示的数量"""
        if self.floating_icon and self.floating_icon.isVisible():
            self.floating_icon.set_count(self.clipboard_service.get_data_count())


    def apply_settings(self, new_settings):
        """应用设置"""
        old_theme = self.settings.get('theme')
        old_output_mode = self.settings.get('output_mode')
        old_color_scheme = self.settings.get('color_scheme')
        self.settings.update(new_settings)

        # 保存设置到数据层
        self.data_model.save_settings(self.settings)

        # 如果输出模式改变，更新业务层
        if new_settings.get('output_mode') != old_output_mode:
            self.clipboard_service.set_output_mode(new_settings.get('output_mode'))
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

        # 更新委托主题
        if hasattr(self, 'item_delegate'):
            self.item_delegate.set_theme(is_dark)

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
        self.data_model.clear_clipboard_data()

        # 停止剪贴板监听器
        if hasattr(self, 'clipboard_listener'):
            self.clipboard_listener.stop()

        # 停止轮询定时器（如果有）
        if hasattr(self, 'clipboard_check_timer'):
            self.clipboard_check_timer.stop()

        if hasattr(self, 'hotkey_listener'):
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass  # 停止快捷键监听器失败

        QApplication.quit()


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
    except Exception:
        return True  # 出错时允许启动


def main():
    # 检查是否已有实例在运行
    if not check_single_instance():
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName('剪贴板助手')
    app.setApplicationDisplayName('剪贴板助手')

    # 设置 Windows AppUserModelID，使通知显示正确的应用名称
    if sys.platform == 'win32':
        try:
            # 设置应用程序用户模型 ID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('剪贴板助手')
        except:
            pass

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
