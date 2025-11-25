"""
渐变标题栏组件
提供可复用的渐变背景标题栏
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QLinearGradient, QColor
from PyQt5.QtCore import QRectF


class GradientHeader(QWidget):
    """
    渐变标题栏组件

    特性:
    - 支持自定义标题
    - 支持暗夜/日间模式
    - 支持配色方案切换
    - 支持拖拽移动窗口
    - 支持自定义按钮
    """

    def __init__(self, title="标题", height=50, parent=None):
        """
        初始化渐变标题栏

        Args:
            title (str): 标题文字
            height (int): 标题栏高度
            parent: 父窗口
        """
        super().__init__(parent)
        self.title = title
        self.is_dark = False
        self.color_scheme = 'pure_blue'
        self.parent_window = parent

        self.setFixedHeight(height)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(15, 0, 15, 0)

        # 标题标签
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(
            'color: white; font-size: 15px; font-weight: 600; background: transparent;'
        )
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def paintEvent(self, event):
        """绘制渐变背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建圆角路径
        path = QPainterPath()
        rect = QRectF(self.rect())
        radius = 10

        # 上半部分圆角矩形
        path.moveTo(rect.left(), rect.bottom())
        path.lineTo(rect.left(), rect.top() + radius)
        path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
        path.lineTo(rect.right() - radius, rect.top())
        path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
        path.lineTo(rect.right(), rect.bottom())
        path.lineTo(rect.left(), rect.bottom())

        # 创建渐变
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())

        # 获取配色方案的颜色
        from themes.theme_manager import get_color_scheme_colors
        color1, color2 = get_color_scheme_colors(self.color_scheme, self.is_dark)
        gradient.setColorAt(0, QColor(color1))
        gradient.setColorAt(1, QColor(color2))

        painter.fillPath(path, gradient)

    def setTitle(self, title):
        """设置标题"""
        self.title = title
        self.title_label.setText(title)

    def setDarkMode(self, is_dark):
        """设置暗夜模式"""
        self.is_dark = is_dark
        self.update()

    def setColorScheme(self, scheme):
        """设置配色方案"""
        self.color_scheme = scheme
        self.update()

    def addButton(self, button):
        """
        添加按钮到标题栏

        Args:
            button (QPushButton): 按钮对象
        """
        self.layout.addWidget(button)

    def addCloseButton(self, callback=None):
        """
        添加关闭按钮

        Args:
            callback: 点击回调函数
        """
        close_btn = QPushButton('×')
        close_btn.setFixedSize(20, 20)
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

        if callback:
            close_btn.clicked.connect(callback)
        elif self.parent_window:
            if isinstance(self.parent_window, QWidget):
                close_btn.clicked.connect(self.parent_window.close)

        self.addButton(close_btn)
        return close_btn

    def addCustomButton(self, icon_text, tooltip, callback=None):
        """
        添加自定义按钮

        Args:
            icon_text (str): 按钮文字或图标
            tooltip (str): 提示文字
            callback: 点击回调函数

        Returns:
            QPushButton: 创建的按钮对象
        """
        btn = QPushButton(icon_text)
        btn.setFixedSize(20, 20)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.35);
            }
        """)

        if callback:
            btn.clicked.connect(callback)

        self.addButton(btn)
        return btn

    def enableDragging(self):
        """启用拖拽移动窗口功能"""
        self.mousePressEvent = self._drag_mouse_press
        self.mouseMoveEvent = self._drag_mouse_move
        self.mouseReleaseEvent = self._drag_mouse_release

    def _drag_mouse_press(self, event):
        """拖拽开始"""
        if event.button() == Qt.LeftButton and self.parent_window:
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def _drag_mouse_move(self, event):
        """拖拽移动"""
        if hasattr(self, 'drag_position') and self.parent_window:
            self.parent_window.move(event.globalPos() - self.drag_position)
            event.accept()

    def _drag_mouse_release(self, event):
        """拖拽结束"""
        if hasattr(self, 'drag_position'):
            delattr(self, 'drag_position')
