"""
可点击标签组件
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class ClickableLabel(QLabel):
    """
    可点击的 QLabel 组件

    用法:
        label = ClickableLabel("点击我", callback=my_function, data="some_data")
    """

    def __init__(self, text, callback=None, data=None, parent=None):
        """
        初始化可点击标签

        Args:
            text (str): 标签文字
            callback: 点击回调函数
            data: 传递给回调函数的数据
            parent: 父组件
        """
        super().__init__(text, parent)
        self.callback = callback
        self.data = data
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            if self.callback:
                if self.data is not None:
                    self.callback(self.data)
                else:
                    self.callback()
        super().mousePressEvent(event)

    def setCallback(self, callback):
        """设置回调函数"""
        self.callback = callback

    def setData(self, data):
        """设置数据"""
        self.data = data
