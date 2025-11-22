"""
多选剪贴板助手 - Windows 桌面版
支持 Ctrl+C 自动添加，批量粘贴（逗号分隔）
"""

import sys
import json
import time
import ctypes
from ctypes import wintypes

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

from datetime import datetime
from pathlib import Path
from functools import partial
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QListWidgetItem,
                             QMessageBox, QMenu, QAction, QSystemTrayIcon)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor
import win32clipboard
import win32con


# Windows API 常量
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12  # Alt
VK_V = 0x56


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT)
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION)
    ]


def send_input_key(vk, up=False):
    """使用 SendInput 发送按键"""
    extra = ctypes.c_ulong(0)
    flags = KEYEVENTF_KEYUP if up else 0

    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = 0
    inp.union.ki.dwFlags = flags
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = ctypes.pointer(extra)

    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def get_clipboard_text():
    """安全地获取剪贴板文本，支持重试"""
    max_retries = 3
    retry_delay = 0.05  # 50ms

    for attempt in range(max_retries):
        try:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    return data
            finally:
                win32clipboard.CloseClipboard()
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print(f"获取剪贴板失败: {e}")
    return None


def set_clipboard_text(text):
    """安全地设置剪贴板文本，支持重试"""
    max_retries = 3
    retry_delay = 0.05  # 50ms

    for attempt in range(max_retries):
        try:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            finally:
                win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print(f"设置剪贴板失败: {e}")
    return False


class ClipboardWindow(QWidget):
    """剪贴板悬浮窗"""

    # 自定义信号
    clipboard_changed_signal = pyqtSignal()
    toggle_window_signal = pyqtSignal()
    quit_app_signal = pyqtSignal()
    do_paste_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        # 数据存储
        self.clipboard_data = []
        self.data_file = Path(__file__).parent / 'data' / 'clipboard_data.json'

        # 拖拽相关
        self.dragging = False
        self.drag_position = QPoint()

        # 状态管理
        self.last_pasted_text = ""
        self.last_paste_time = 0  # 最后一次粘贴的时间戳
        self.paste_ignore_until = 0  # 时间戳，在此之前忽略剪贴板变化

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

    def register_clipboard_listener(self):
        """注册 Windows 剪贴板监听器"""
        # 使用定时器轮询剪贴板（最可靠的方式）
        self.last_clipboard_text = get_clipboard_text() or ""
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
            # 处理文本
            texts = self.process_clipboard_text(text)

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
                self.update_list()
                self.save_data()

                # 显示通知
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
            self.show_notification('剪贴板为空')
            return

        # 拼接所有文本
        texts = [item['text'] if isinstance(item, dict) else item for item in self.clipboard_data]
        combined_text = ','.join(texts)

        # 记录粘贴的内容和时间，防止被重新添加到列表
        self.last_pasted_text = combined_text
        self.last_paste_time = time.time()

        # 设置忽略时间（1.5秒内忽略剪贴板变化）
        self.paste_ignore_until = time.time() + 1.5

        # 设置剪贴板
        if set_clipboard_text(combined_text):
            self.last_clipboard_text = combined_text
            # 延迟250ms执行粘贴，确保剪贴板更新完成且用户释放快捷键
            QTimer.singleShot(250, self._execute_paste)
        else:
            self.show_notification('设置剪贴板失败')

    def _execute_paste(self):
        """执行实际的粘贴操作"""
        try:
            # 先释放所有修饰键（Ctrl、Alt、Shift）
            send_input_key(VK_CONTROL, up=True)
            send_input_key(VK_MENU, up=True)
            send_input_key(VK_SHIFT, up=True)
            time.sleep(0.05)

            # 模拟 Ctrl+V
            send_input_key(VK_CONTROL, up=False)
            time.sleep(0.02)
            send_input_key(VK_V, up=False)
            time.sleep(0.02)
            send_input_key(VK_V, up=True)
            time.sleep(0.02)
            send_input_key(VK_CONTROL, up=True)

            # 显示成功通知
            texts_count = len(self.clipboard_data)
            self.show_notification(f'已粘贴 {texts_count} 项内容')
        except Exception as e:
            print(f"执行粘贴失败: {e}")
            self.show_notification('粘贴失败')

    def process_clipboard_text(self, text):
        """处理剪贴板文本"""
        if not text:
            return []

        if '\n' in text or '\r' in text:
            lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
            return [line.strip() for line in lines if line.strip()]
        else:
            return [text.strip()] if text.strip() else []

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
        self.main_container.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 10px;
            }
        """)

        container_shadow = self.create_shadow()
        self.main_container.setGraphicsEffect(container_shadow)

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        header = self.create_header()
        container_layout.addWidget(header)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(4)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                padding: 8px;
                font-size: 14px;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding: 0px;
            }
            QListWidget::item:disabled {
                background: transparent;
                color: #909399;
                border: none;
            }
            QListWidget::item:hover {
                background: transparent;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.3),
                    stop:1 rgba(118, 75, 162, 0.3));
                min-height: 30px;
                border-radius: 4px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.6),
                    stop:1 rgba(118, 75, 162, 0.6));
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        container_layout.addWidget(self.list_widget)

        self.main_container.setLayout(container_layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_container)
        self.setLayout(outer_layout)

    def create_header(self):
        """创建头部"""
        from PyQt5.QtGui import QPainter, QPainterPath, QLinearGradient

        class HeaderWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.collapsed = False

            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                from PyQt5.QtCore import QRectF

                path = QPainterPath()
                rect = QRectF(self.rect())

                if self.collapsed:
                    path.addRoundedRect(rect, 10, 10)
                else:
                    radius = 10
                    path.moveTo(rect.left(), rect.bottom())
                    path.lineTo(rect.left(), rect.top() + radius)
                    path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
                    path.lineTo(rect.right() - radius, rect.top())
                    path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
                    path.lineTo(rect.right(), rect.bottom())
                    path.lineTo(rect.left(), rect.bottom())

                gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
                gradient.setColorAt(0, QColor('#667eea'))
                gradient.setColorAt(1, QColor('#764ba2'))
                painter.fillPath(path, gradient)

            def setCollapsed(self, collapsed):
                self.collapsed = collapsed
                self.update()

        header = HeaderWidget()
        header.setFixedHeight(50)
        header.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.35);
            }
            QLabel {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 600;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 0, 12, 0)

        self.title_label = QLabel('剪贴板 (0)')
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.toggle_btn = QPushButton('−')
        self.toggle_btn.setFixedSize(20, 20)
        self.toggle_btn.setToolTip('折叠/展开')
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.35);
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.toggle_btn)

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
        clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 100, 100, 0.6);
            }
        """)
        layout.addWidget(clear_btn)

        close_btn = QPushButton('×')
        close_btn.setFixedSize(20, 20)
        close_btn.setToolTip('隐藏窗口')
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 100, 100, 0.8);
            }
        """)
        close_btn.clicked.connect(self.hide_window)
        layout.addWidget(close_btn)

        header.setLayout(layout)
        header.mousePressEvent = self.header_mouse_press
        header.mouseMoveEvent = self.header_mouse_move
        header.mouseReleaseEvent = self.header_mouse_release

        self.header = header
        return header

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

        tray_menu = QMenu()
        show_action = QAction('显示窗口', self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)

        hide_action = QAction('隐藏窗口', self)
        hide_action.triggered.connect(self.hide_window)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        quit_action = QAction('退出程序', self)
        quit_action.triggered.connect(self.do_quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        self.tray_icon.setToolTip('剪贴板助手\nCtrl+Shift+C: 显示/隐藏\nCtrl+Space: 批量粘贴\nCtrl+Shift+Q: 退出')

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.do_toggle_window()

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

    def toggle_collapse(self):
        if self.list_widget.isVisible():
            self.list_widget.hide()
            self.toggle_btn.setText('+')
            self.setFixedHeight(60)
            self.main_container.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border: none;
                    border-radius: 10px;
                }
            """)
            self.header.setCollapsed(True)
        else:
            self.list_widget.show()
            self.toggle_btn.setText('−')
            self.setFixedHeight(560)
            self.main_container.setStyleSheet("""
                QWidget {
                    background: #ffffff;
                    border: 1px solid rgba(102, 126, 234, 0.3);
                    border-radius: 10px;
                }
            """)
            self.header.setCollapsed(False)

    def update_list(self):
        """更新列表显示"""
        self.list_widget.clear()
        self.title_label.setText(f'剪贴板 ({len(self.clipboard_data)})')

        if not self.clipboard_data:
            item = QListWidgetItem('暂无数据')
            item.setFlags(Qt.NoItemFlags)
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor('#909399'))
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
        widget.setStyleSheet("""
            QWidget {
                background: #f5f7fa;
                border: none;
                border-radius: 6px;
            }
            QWidget:hover {
                background: #e8edf5;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        label = QLabel(text)
        label.setWordWrap(False)
        label.setFixedWidth(200)
        label.setToolTip(text)
        label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #303133;
                font-size: 13px;
            }
        """)
        label.setTextFormat(Qt.PlainText)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font_metrics = label.fontMetrics()
        elided_text = font_metrics.elidedText(text, Qt.ElideRight, 200)
        label.setText(elided_text)

        layout.addWidget(label)
        layout.addStretch()

        time_label = QLabel(timestamp)
        time_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #909399;
                font-size: 12px;
            }
        """)
        time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(time_label)

        delete_btn = QPushButton('×')
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #f56c6c;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #f34040;
            }
        """)
        delete_btn.clicked.connect(partial(self.remove_item_by_text, text))
        layout.addWidget(delete_btn)

        widget.setLayout(layout)
        return widget

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
            self.update_list()
            self.save_data()
            set_clipboard_text('')
            self.last_clipboard_text = ''

    def hide_window(self):
        self.hide()
        self.show_notification('程序已最小化到系统托盘')

    def show_window(self):
        self.show()
        self.activateWindow()
        self.raise_()

    def do_toggle_window(self):
        if self.isVisible():
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

    def closeEvent(self, event):
        self.save_data()
        event.ignore()
        self.hide()

    def do_quit_app(self):
        """退出程序"""
        self.save_data()

        if hasattr(self, 'clipboard_check_timer'):
            self.clipboard_check_timer.stop()

        if hasattr(self, 'hotkey_listener'):
            try:
                self.hotkey_listener.stop()
            except Exception as e:
                print(f"停止快捷键监听器失败: {e}")

        QApplication.quit()


def main():
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
