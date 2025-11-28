"""
剪贴板列表项委托
使用 QStyledItemDelegate 实现高性能的虚拟化列表渲染
"""

from PyQt5.QtWidgets import QStyledItemDelegate, QStyle, QApplication
from PyQt5.QtCore import Qt, QRect, QSize, QEvent, QModelIndex
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QPen, QBrush


class ClipboardItemDelegate(QStyledItemDelegate):
    """剪贴板列表项委托 - 高性能虚拟化渲染"""

    # 常量定义
    ITEM_HEIGHT = 44
    ITEM_MARGIN = 4
    CONTENT_MARGIN_H = 12
    CONTENT_MARGIN_V = 8
    DELETE_BTN_SIZE = 20
    TEXT_WIDTH = 200
    SPACING = 12

    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.is_dark = False
        self.hovered_index = -1
        self.hovered_delete_index = -1  # 鼠标悬停在删除按钮上的索引

        # 回调函数
        self.on_delete_click = None  # 点击删除按钮回调

    def set_theme(self, is_dark):
        """设置主题"""
        self.is_dark = is_dark

    def set_hovered_index(self, index):
        """设置悬停索引"""
        self.hovered_index = index

    def set_hovered_delete_index(self, index):
        """设置悬停删除按钮索引"""
        self.hovered_delete_index = index

    def sizeHint(self, option, index):
        """返回项目大小"""
        if option is None:
            # 直接调用时返回默认大小
            return QSize(300, self.ITEM_HEIGHT)
        return QSize(option.rect.width(), self.ITEM_HEIGHT)

    def paint(self, painter, option, index):
        """绘制列表项"""
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # 获取数据
        data = index.data(Qt.UserRole)
        if not data:
            painter.restore()
            return

        text = data.get('text', '')
        timestamp = data.get('timestamp', '')
        row = index.row()

        # 计算绘制区域
        rect = option.rect
        content_rect = QRect(
            rect.x() + self.ITEM_MARGIN,
            rect.y() + 2,
            rect.width() - self.ITEM_MARGIN * 2,
            rect.height() - 4
        )

        # 判断是否悬停
        is_hovered = row == self.hovered_index

        # 绘制背景
        self.draw_background(painter, content_rect, is_hovered)

        # 绘制文本
        self.draw_text(painter, content_rect, text)

        # 绘制时间戳
        self.draw_timestamp(painter, content_rect, timestamp)

        # 绘制删除按钮
        self.draw_delete_button(painter, content_rect, row)

        painter.restore()

    def draw_background(self, painter, rect, is_hovered):
        """绘制背景"""
        if self.is_dark:
            bg_color = QColor('#3d3d3d') if is_hovered else QColor('#2d2d2d')
        else:
            bg_color = QColor('#e8edf5') if is_hovered else QColor('#f5f7fa')

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, 6, 6)

    def draw_text(self, painter, rect, text):
        """绘制文本"""
        if self.is_dark:
            text_color = QColor('#e0e0e0')
        else:
            text_color = QColor('#303133')

        painter.setPen(text_color)
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)

        # 文本区域
        text_rect = QRect(
            rect.x() + self.CONTENT_MARGIN_H,
            rect.y() + self.CONTENT_MARGIN_V,
            self.TEXT_WIDTH,
            rect.height() - self.CONTENT_MARGIN_V * 2
        )

        # 省略过长文本
        metrics = QFontMetrics(font)
        elided_text = metrics.elidedText(text, Qt.ElideRight, self.TEXT_WIDTH)

        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, elided_text)

    def draw_timestamp(self, painter, rect, timestamp):
        """绘制时间戳"""
        if self.is_dark:
            time_color = QColor('#888888')
        else:
            time_color = QColor('#909399')

        painter.setPen(time_color)
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)

        # 时间区域（在删除按钮左边）
        time_rect = QRect(
            rect.x() + self.CONTENT_MARGIN_H + self.TEXT_WIDTH + self.SPACING,
            rect.y() + self.CONTENT_MARGIN_V,
            60,
            rect.height() - self.CONTENT_MARGIN_V * 2
        )

        painter.drawText(time_rect, Qt.AlignRight | Qt.AlignVCenter, timestamp)

    def draw_delete_button(self, painter, rect, row):
        """绘制删除按钮"""
        # 删除按钮区域
        btn_x = rect.right() - self.CONTENT_MARGIN_H - self.DELETE_BTN_SIZE
        btn_y = rect.y() + (rect.height() - self.DELETE_BTN_SIZE) // 2
        btn_rect = QRect(btn_x, btn_y, self.DELETE_BTN_SIZE, self.DELETE_BTN_SIZE)

        # 判断是否悬停在删除按钮上
        is_delete_hovered = row == self.hovered_delete_index

        # 按钮背景
        if is_delete_hovered:
            bg_color = QColor('#f34040')
        else:
            bg_color = QColor('#f56c6c')

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(btn_rect, 10, 10)

        # 绘制 × 符号
        painter.setPen(QPen(QColor('white'), 1.5))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(btn_rect, Qt.AlignCenter, '×')

    def get_delete_button_rect(self, option):
        """获取删除按钮的区域"""
        rect = option.rect
        content_rect = QRect(
            rect.x() + self.ITEM_MARGIN,
            rect.y() + 2,
            rect.width() - self.ITEM_MARGIN * 2,
            rect.height() - 4
        )

        btn_x = content_rect.right() - self.CONTENT_MARGIN_H - self.DELETE_BTN_SIZE
        btn_y = content_rect.y() + (content_rect.height() - self.DELETE_BTN_SIZE) // 2

        return QRect(btn_x, btn_y, self.DELETE_BTN_SIZE, self.DELETE_BTN_SIZE)

    def editorEvent(self, event, model, option, index):
        """处理鼠标事件"""
        if event.type() == QEvent.MouseButtonRelease:
            # 获取删除按钮区域
            delete_rect = self.get_delete_button_rect(option)

            if delete_rect.contains(event.pos()):
                # 点击了删除按钮
                if self.on_delete_click:
                    data = index.data(Qt.UserRole)
                    if data:
                        self.on_delete_click(data.get('text', ''))
                return True
            # 移除了点击项目本身的粘贴功能

        return super().editorEvent(event, model, option, index)
