"""
剪贴板监听器 - macOS/跨平台版本
使用 PyQt5 QClipboard 的 dataChanged 信号
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal


class ClipboardListener(QObject):
    """
    剪贴板监听器 - 跨平台版本
    使用 Qt 的剪贴板变化信号
    """

    # 剪贴板变化信号
    clipboard_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._clipboard = None
        self._last_text = None  # 用于去重

    def start(self):
        """开始监听剪贴板"""
        if self._running:
            return True

        try:
            self._clipboard = QApplication.clipboard()
            if self._clipboard:
                # 记录当前剪贴板内容，用于后续去重
                self._last_text = self._clipboard.text()
                # 连接剪贴板变化信号
                self._clipboard.dataChanged.connect(self._on_clipboard_changed)
                self._running = True
                return True
            return False
        except Exception:
            return False

    def stop(self):
        """停止监听剪贴板"""
        if not self._running:
            return

        try:
            if self._clipboard:
                self._clipboard.dataChanged.disconnect(self._on_clipboard_changed)
        except Exception:
            pass

        self._running = False
        self._clipboard = None

    def _on_clipboard_changed(self):
        """剪贴板内容变化时的回调"""
        try:
            # 获取当前剪贴板文本
            current_text = self._clipboard.text() if self._clipboard else None

            # 检查内容是否真的变化了（去重）
            if current_text != self._last_text:
                self._last_text = current_text
                self.clipboard_changed.emit()
        except Exception:
            # 即使出错也发出信号，让上层处理
            self.clipboard_changed.emit()

    def is_running(self):
        """检查监听器是否正在运行"""
        return self._running
