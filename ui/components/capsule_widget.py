"""
胶囊组件
用于主窗口最小化后显示在屏幕右侧的胶囊状图标
"""

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPainterPath, QLinearGradient


class CapsuleWidget(QWidget):
    """胶囊悬浮组件"""

    # 信号：双击胶囊时发出
    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.count = 0  # 复制记录条数
        self.is_expanded = False  # 是否展开状态
        self.is_dark = False  # 是否暗夜模式
        self.color_scheme = 'pure_blue'  # 配色方案
        self.is_animating = False  # 是否正在动画中

        # 胶囊尺寸
        self.collapsed_width = 6  # 收起宽度（胶囊条）
        self.expanded_width = 60  # 展开宽度（圆形图标）
        self.capsule_height = 100  # 高度

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 窗口设置
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 初始位置和大小（收起状态）
        self.setFixedSize(self.collapsed_width, self.capsule_height)

        # 设置鼠标追踪
        self.setMouseTracking(True)

        # 创建动画
        self.expand_animation = QPropertyAnimation(self, b"geometry")
        self.expand_animation.setDuration(200)
        self.expand_animation.finished.connect(self.on_animation_finished)

    def on_animation_finished(self):
        """动画结束"""
        self.is_animating = False

    def set_count(self, count):
        """设置复制条数"""
        self.count = count
        self.update()

    def set_theme(self, is_dark, color_scheme):
        """设置主题"""
        self.is_dark = is_dark
        self.color_scheme = color_scheme
        self.update()

    def get_colors(self):
        """获取配色方案颜色"""
        from themes.theme_manager import get_color_scheme_colors
        return get_color_scheme_colors(self.color_scheme, self.is_dark)

    def position_at_screen_edge(self):
        """定位到屏幕右侧边缘"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()

        # 垂直居中，靠右显示
        x = screen.width() - self.width()
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def expand(self):
        """展开胶囊（显示图标）"""
        if self.is_expanded or self.is_animating:
            return

        self.is_expanded = True
        self.is_animating = True
        screen_width = self.screen().geometry().width()
        current_pos = self.pos()

        # 从右侧边缘展开
        start_rect = QRect(
            screen_width - self.collapsed_width,
            current_pos.y(),
            self.collapsed_width,
            self.capsule_height
        )

        end_rect = QRect(
            screen_width - self.expanded_width,
            current_pos.y(),
            self.expanded_width,
            self.capsule_height
        )

        self.expand_animation.setStartValue(start_rect)
        self.expand_animation.setEndValue(end_rect)
        self.expand_animation.start()

    def collapse(self):
        """收起胶囊（显示细条）"""
        if not self.is_expanded or self.is_animating:
            return

        self.is_expanded = False
        self.is_animating = True
        screen_width = self.screen().geometry().width()
        current_pos = self.pos()

        # 收起到右侧边缘
        start_rect = QRect(
            current_pos.x(),
            current_pos.y(),
            self.expanded_width,
            self.capsule_height
        )

        end_rect = QRect(
            screen_width - self.collapsed_width,
            current_pos.y(),
            self.collapsed_width,
            self.capsule_height
        )

        self.expand_animation.setStartValue(start_rect)
        self.expand_animation.setEndValue(end_rect)
        self.expand_animation.start()

    def enterEvent(self, event):
        """鼠标进入"""
        self.expand()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开"""
        self.collapse()
        super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """双击事件"""
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def paintEvent(self, event):
        """绘制胶囊"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 获取配色
        color1, color2 = self.get_colors()

        if self.is_expanded:
            # 展开状态：绘制圆形图标
            self.draw_expanded(painter, color1, color2)
        else:
            # 收起状态：绘制胶囊条
            self.draw_collapsed(painter, color1, color2)

    def draw_collapsed(self, painter, color1, color2):
        """绘制收起状态（细条）"""
        width = self.width()
        height = self.height()

        # 创建圆角矩形路径
        path = QPainterPath()
        radius = width / 2
        path.addRoundedRect(0, 0, width, height, radius, radius)

        # 渐变填充
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(color1))
        gradient.setColorAt(1, QColor(color2))

        painter.fillPath(path, gradient)

    def draw_expanded(self, painter, color1, color2):
        """绘制展开状态（圆形图标 + 数字）"""
        width = self.width()
        height = self.height()

        # 绘制圆形背景
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 5

        # 创建圆形路径
        path = QPainterPath()
        path.addEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # 渐变填充
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor(color1))
        gradient.setColorAt(1, QColor(color2))

        painter.fillPath(path, gradient)

        # 绘制数字
        painter.setPen(QColor('white'))

        # 根据数字大小调整字体
        if self.count < 10:
            font_size = 20
        elif self.count < 100:
            font_size = 16
        else:
            font_size = 12

        font = QFont('Arial', font_size, QFont.Bold)
        painter.setFont(font)

        # 居中绘制数字
        text = str(self.count)
        text_rect = painter.fontMetrics().boundingRect(text)
        text_x = center_x - text_rect.width() // 2
        text_y = center_y + text_rect.height() // 2 - 2

        painter.drawText(text_x, text_y, text)
