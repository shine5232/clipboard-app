"""
自定义托盘菜单组件
美观的右键菜单，带图标和悬停效果
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QFont, QPen, QPixmap, QIcon


class TrayMenuItem(QWidget):
    """托盘菜单项"""

    clicked = pyqtSignal()

    def __init__(self, icon_type, text, color="#667eea", is_danger=False, is_dark=False, parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.text = text
        self.color = color  # 配色方案颜色
        self.is_danger = is_danger
        self.is_hovered = False
        self.is_dark = is_dark

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setFixedHeight(32)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(8)

        # 图标
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        self.update_icon()
        layout.addWidget(self.icon_label)

        # 文本
        self.text_label = QLabel(self.text)
        self.text_label.setFont(QFont('Microsoft YaHei', 9))
        layout.addWidget(self.text_label)

        layout.addStretch()
        self.setLayout(layout)

        self.update_style()

    def update_icon(self):
        """更新图标"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 根据状态选择颜色
        if self.is_danger:
            color = QColor("#e74c3c")
        else:
            # 使用配色方案颜色
            color = QColor(self.color)

        pen = QPen(color, 1.5)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        if self.icon_type == "window":
            # 窗口图标
            painter.drawRoundedRect(2, 3, 12, 10, 2, 2)
            painter.drawLine(2, 6, 14, 6)
            painter.setBrush(color)
            painter.drawEllipse(4, 4, 2, 2)
            painter.drawEllipse(7, 4, 2, 2)

        elif self.icon_type == "exit":
            # 退出图标
            painter.drawRect(5, 2, 8, 12)
            painter.drawLine(5, 2, 5, 14)
            painter.drawLine(5, 2, 13, 2)
            painter.drawLine(5, 14, 13, 14)
            # 箭头
            painter.drawLine(1, 8, 8, 8)
            painter.drawLine(1, 8, 4, 5)
            painter.drawLine(1, 8, 4, 11)

        elif self.icon_type == "settings":
            # 设置图标（齿轮）
            import math
            center_x, center_y = 8, 8
            painter.drawEllipse(5, 5, 6, 6)
            for i in range(8):
                angle = i * math.pi / 4
                x1 = center_x + 3 * math.cos(angle)
                y1 = center_y + 3 * math.sin(angle)
                x2 = center_x + 6 * math.cos(angle)
                y2 = center_y + 6 * math.sin(angle)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.end()
        self.icon_label.setPixmap(pixmap)

    def update_style(self):
        """更新样式"""
        if self.is_hovered:
            bg_color = "rgba(231, 76, 60, 0.1)" if self.is_danger else "rgba(102, 126, 234, 0.1)"
        else:
            bg_color = "transparent"

        # 文本颜色：危险项用红色，普通项使用配色方案颜色
        if self.is_danger:
            text_color = "#e74c3c"
        else:
            text_color = self.color

        self.setStyleSheet(f"""
            TrayMenuItem {{
                background: {bg_color};
                border-radius: 6px;
            }}
        """)
        self.text_label.setStyleSheet(f"color: {text_color}; background: transparent;")

    def set_dark_mode(self, is_dark):
        """设置暗夜模式"""
        self.is_dark = is_dark
        self.update_style()
        self.update_icon()

    def set_color(self, color):
        """设置配色方案颜色"""
        self.color = color
        self.update_style()
        self.update_icon()

    def enterEvent(self, event):
        """鼠标进入"""
        self.is_hovered = True
        self.update_style()
        self.update_icon()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开"""
        self.is_hovered = False
        self.update_style()
        self.update_icon()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """鼠标点击"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class TrayMenu(QWidget):
    """自定义托盘菜单"""

    # 信号
    show_window_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark = False
        self.color_scheme = 'pure_blue'
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowFlags(
            Qt.Popup |
            Qt.FramelessWindowHint |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedWidth(150)  # 设置弹窗固定宽度

        # 主容器
        self.container = QWidget()
        self.container.setObjectName("trayMenuContainer")

        # 添加阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.container.setGraphicsEffect(shadow)

        # 获取配色方案颜色
        from themes.theme_manager import get_color_scheme_colors
        color1, _ = get_color_scheme_colors(self.color_scheme, self.is_dark)

        # 容器布局
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(6, 6, 6, 6)
        container_layout.setSpacing(2)

        # 菜单项
        self.show_item = TrayMenuItem("window", "打开主界面", color1, is_dark=self.is_dark)
        self.show_item.clicked.connect(self.on_show_clicked)
        container_layout.addWidget(self.show_item)

        self.quit_item = TrayMenuItem("exit", "退出程序", "#e74c3c", is_danger=True, is_dark=self.is_dark)
        self.quit_item.clicked.connect(self.on_quit_clicked)
        container_layout.addWidget(self.quit_item)

        self.container.setLayout(container_layout)

        # 外层布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)

        self.update_style()

    def update_style(self):
        """更新样式"""
        bg_color = "#2d2d2d" if self.is_dark else "#ffffff"
        border_color = "rgba(255,255,255,0.1)" if self.is_dark else "rgba(0,0,0,0.08)"

        self.container.setStyleSheet(f"""
            #trayMenuContainer {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
        """)

        # 获取配色方案颜色并更新菜单项
        from themes.theme_manager import get_color_scheme_colors
        color1, _ = get_color_scheme_colors(self.color_scheme, self.is_dark)

        # 更新菜单项的暗夜模式和颜色
        if hasattr(self, 'show_item'):
            self.show_item.set_dark_mode(self.is_dark)
            self.show_item.set_color(color1)
        if hasattr(self, 'quit_item'):
            self.quit_item.set_dark_mode(self.is_dark)

    def set_theme(self, is_dark, color_scheme):
        """设置主题"""
        self.is_dark = is_dark
        self.color_scheme = color_scheme
        self.update_style()

    def on_show_clicked(self):
        """点击显示窗口"""
        self.hide()
        self.show_window_clicked.emit()

    def on_quit_clicked(self):
        """点击退出"""
        self.hide()
        self.quit_clicked.emit()

    def show_at_cursor(self):
        """在鼠标位置显示菜单"""
        from PyQt5.QtGui import QCursor
        from PyQt5.QtWidgets import QApplication

        # 调整大小
        self.adjustSize()

        # 获取鼠标位置和屏幕信息
        cursor_pos = QCursor.pos()
        screen = QApplication.desktop().screenGeometry()

        # 计算菜单位置，确保不超出屏幕
        menu_width = self.width()
        menu_height = self.height()

        x = cursor_pos.x()
        y = cursor_pos.y() - menu_height  # 在鼠标上方显示

        # 边界检查
        if x + menu_width > screen.width():
            x = screen.width() - menu_width
        if x < 0:
            x = 0
        if y < 0:
            y = cursor_pos.y()  # 如果上方空间不够，显示在下方
        if y + menu_height > screen.height():
            y = screen.height() - menu_height

        self.move(x, y)
        self.show()
        self.activateWindow()
