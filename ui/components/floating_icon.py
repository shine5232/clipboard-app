"""
桌面浮动图标组件
可拖拽的圆形图标，拖到屏幕右侧时自动吸附并收缩为胶囊状
"""

from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QPainterPath, QLinearGradient, QRadialGradient


class FloatingIcon(QWidget):
    """桌面浮动图标组件"""

    # 信号
    double_clicked = pyqtSignal()
    mouse_entered = pyqtSignal()  # 鼠标进入信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.count = 0  # 复制记录条数
        self.is_dark = False  # 是否暗夜模式
        self.color_scheme = 'pure_blue'  # 配色方案

        # 截图相关
        self.window_pixmap = None  # 主窗口截图

        # 拖拽相关
        self.dragging = False
        self.drag_start_pos = QPoint()

        # 胶囊模式相关
        self.is_capsule_mode = False  # 是否为胶囊模式
        self.is_animating = False  # 是否正在动画中
        self.allow_hover_restore = False  # 是否允许鼠标悬停恢复（防止飞出时立即触发）
        self.edge_threshold = 60  # 靠近边缘的距离阈值（像素）- 减小到60px，更不容易误触发

        # 图标尺寸
        self.icon_size = 80  # 圆形图标大小
        self.capsule_width = 8  # 胶囊宽度
        self.capsule_height = 80  # 胶囊高度（改为80，与圆形图标相同）

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

        # 初始大小（圆形图标）
        self.setGeometry(0, 0, self.icon_size, self.icon_size)  # 使用 setGeometry 而不是 setFixedSize

        # 设置鼠标追踪
        self.setMouseTracking(True)

        # 创建动画
        self.morph_animation = QPropertyAnimation(self, b"geometry")
        self.morph_animation.setDuration(300)
        self.morph_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.morph_animation.finished.connect(self.on_animation_finished)

        # 延迟检测定时器（防止频繁切换）
        self.edge_check_timer = QTimer()
        self.edge_check_timer.setSingleShot(True)
        self.edge_check_timer.timeout.connect(self.check_edge_position)

        # 初始应用阴影（仅胶囊模式）
        self.update_shadow()

    def update_shadow(self):
        """更新阴影效果（仅胶囊模式有阴影）"""
        try:
            if self.is_capsule_mode:
                # 胶囊模式：添加左侧阴影
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(15)
                shadow.setColor(QColor(0, 0, 0, 100))
                shadow.setOffset(-3, 0)  # 向左偏移3px
                self.setGraphicsEffect(shadow)
            else:
                # 圆形模式：不使用阴影，避免更新问题
                self.setGraphicsEffect(None)
        except RuntimeError:
            # 忽略阴影对象已删除的错误
            pass

    def set_count(self, count):
        """设置复制条数"""
        if self.count != count:  # 只有数量变化时才更新
            self.count = count
            self.repaint()

    def set_theme(self, is_dark, color_scheme):
        """设置主题"""
        self.is_dark = is_dark
        self.color_scheme = color_scheme
        self.update()

    def set_window_pixmap(self, pixmap):
        """设置主窗口截图"""
        self.window_pixmap = pixmap
        self.update()

    def clear_window_pixmap(self):
        """清除主窗口截图"""
        self.window_pixmap = None
        self.update()

    def get_colors(self):
        """获取配色方案颜色"""
        from themes.theme_manager import get_color_scheme_colors
        return get_color_scheme_colors(self.color_scheme, self.is_dark)

    def position_at_center(self):
        """定位到屏幕中央"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()

        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def check_edge_position(self):
        """检查是否靠近屏幕右侧边缘"""
        if self.is_animating:
            return

        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()

        current_x = self.x()
        screen_width = screen.width()

        # 检查是否靠近右侧边缘
        distance_to_right = screen_width - (current_x + self.width())

        if distance_to_right < self.edge_threshold:
            # 靠近右侧边缘，切换到胶囊模式
            if not self.is_capsule_mode:
                self.morph_to_capsule()
        else:
            # 远离边缘，切换回圆形模式
            if self.is_capsule_mode:
                self.morph_to_circle()

    def morph_to_capsule(self):
        """变形为胶囊"""
        if self.is_capsule_mode or self.is_animating:
            return

        self.is_capsule_mode = True
        self.is_animating = True

        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QRect
        screen = QApplication.desktop().screenGeometry()

        # 当前位置
        current_rect = self.geometry()

        # 目标位置：屏幕右侧边缘，垂直居中
        target_x = screen.width() - self.capsule_width
        target_y = (screen.height() - self.capsule_height) // 2
        target_rect = QRect(target_x, target_y, self.capsule_width, self.capsule_height)

        # 执行变形动画
        self.morph_animation.setStartValue(current_rect)
        self.morph_animation.setEndValue(target_rect)
        self.morph_animation.start()

    def morph_to_circle(self):
        """变形为圆形"""
        if not self.is_capsule_mode or self.is_animating:
            return

        self.is_capsule_mode = False
        self.is_animating = True

        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QRect

        screen = QApplication.desktop().screenGeometry()

        # 当前位置
        current_rect = self.geometry()

        # 目标位置：展开为圆形，向左移动一定距离，确保不在边缘阈值内
        # 让圆形图标的右边缘距离屏幕右边缘 70px（略大于阈值60px，避免误触发）
        target_x = screen.width() - self.icon_size - 70
        target_y = current_rect.y() + (self.capsule_height - self.icon_size) // 2
        target_rect = QRect(target_x, target_y, self.icon_size, self.icon_size)

        # 执行变形动画
        self.morph_animation.setStartValue(current_rect)
        self.morph_animation.setEndValue(target_rect)
        self.morph_animation.start()

    def on_animation_finished(self):
        """动画结束"""
        self.is_animating = False
        self.update_shadow()  # 更新阴影
        self.update()

    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            # 保持阴影，不移除
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.dragging and event.buttons() & Qt.LeftButton:
            # 移动窗口，保持阴影不变
            new_pos = event.globalPos() - self.drag_start_pos
            self.move(new_pos)

            # 拖拽时不检测边缘，避免频繁触发动画导致错误
            # 只在释放鼠标时检测
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.LeftButton:
            self.dragging = False

            # 最后检查一次边缘位置
            self.check_edge_position()

            event.accept()

    def mouseDoubleClickEvent(self, event):
        """双击事件"""
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def enterEvent(self, event):
        """鼠标进入"""
        # 如果是胶囊模式且允许悬停恢复，鼠标悬停时发送信号
        if self.is_capsule_mode and not self.is_animating and self.allow_hover_restore:
            self.mouse_entered.emit()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开"""
        # 不再自动收缩，保持圆形状态
        # 只有通过拖拽到右侧边缘才会变为胶囊
        super().leaveEvent(event)

    def paintEvent(self, event):
        """绘制图标"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 如果有截图，优先绘制截图
        if self.window_pixmap:
            # 绘制缩放的截图
            scaled_pixmap = self.window_pixmap.scaled(
                self.width(), self.height(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pixmap)
            return

        # 获取配色
        color1, color2 = self.get_colors()

        if self.is_capsule_mode:
            # 绘制胶囊状态
            self.draw_capsule(painter, color1, color2)
        else:
            # 绘制圆形图标
            self.draw_circle_icon(painter, color1, color2)

    def draw_capsule(self, painter, color1, color2):
        """绘制胶囊状态"""
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

    def draw_circle_icon(self, painter, color1, color2):
        """绘制圆形图标（简洁版）"""
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 10  # 留出阴影空间

        # 绘制主圆形（渐变）
        main_gradient = QLinearGradient(0, 0, width, height)
        main_gradient.setColorAt(0, QColor(color1))
        main_gradient.setColorAt(1, QColor(color2))

        painter.setBrush(main_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(center_x - radius), int(center_y - radius),
                           int(radius * 2), int(radius * 2))

        # 绘制数字
        painter.setPen(QColor(255, 255, 255))  # 白色

        # 根据数字大小调整字体
        if self.count < 10:
            font_size = 24  # 减小字体（原28）
        elif self.count < 100:
            font_size = 18  # 减小字体（原22）
        elif self.count < 1000:
            font_size = 14  # 减小字体（原18）
        else:
            font_size = 12  # 更多位数使用更小字体

        font = QFont('Arial', font_size, QFont.Bold)
        painter.setFont(font)

        # 居中绘制数字 - 使用 drawText 的矩形版本更可靠
        text = str(self.count)
        from PyQt5.QtCore import QRectF, Qt as QtCore
        text_rect = QRectF(0, 0, width, height)
        painter.drawText(text_rect, QtCore.AlignCenter, text)
