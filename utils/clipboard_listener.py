"""
Windows 剪贴板监听器
使用 AddClipboardFormatListener API 替代轮询
"""

import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, Qt


# Windows API 常量
WM_CLIPBOARDUPDATE = 0x031D

# 加载 Windows API
user32 = ctypes.windll.user32

# 定义函数签名
AddClipboardFormatListener = user32.AddClipboardFormatListener
AddClipboardFormatListener.argtypes = [wintypes.HWND]
AddClipboardFormatListener.restype = wintypes.BOOL

RemoveClipboardFormatListener = user32.RemoveClipboardFormatListener
RemoveClipboardFormatListener.argtypes = [wintypes.HWND]
RemoveClipboardFormatListener.restype = wintypes.BOOL


class ClipboardListener(QWidget):
    """
    剪贴板监听器
    使用 Windows AddClipboardFormatListener API 监听剪贴板变化
    """

    # 剪贴板变化信号
    clipboard_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置为完全隐藏的窗口
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(1, 1)
        self.move(-100, -100)  # 移到屏幕外

        self._registered = False

    def start(self):
        """开始监听剪贴板"""
        if self._registered:
            return True

        # 显示窗口以获取有效的窗口句柄
        self.show()

        # 获取窗口句柄
        hwnd = int(self.winId())

        # 注册剪贴板监听器
        result = AddClipboardFormatListener(hwnd)
        if result:
            self._registered = True
            return True
        else:
            self.hide()
            return False

    def stop(self):
        """停止监听剪贴板"""
        if not self._registered:
            return

        hwnd = int(self.winId())
        RemoveClipboardFormatListener(hwnd)
        self._registered = False
        self.hide()

    def nativeEvent(self, eventType, message):
        """处理 Windows 原生消息"""
        if eventType == b'windows_generic_MSG':
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == WM_CLIPBOARDUPDATE:
                # 剪贴板内容已更新，发出信号
                self.clipboard_changed.emit()
                return True, 0

        return super().nativeEvent(eventType, message)

    def closeEvent(self, event):
        """关闭时停止监听"""
        self.stop()
        super().closeEvent(event)
