"""
剪贴板工具模块 - macOS/跨平台版本
使用 PyQt5 QClipboard 进行剪贴板操作
"""

import time
import platform
from PyQt5.QtWidgets import QApplication


def get_clipboard_text():
    """
    安全地获取剪贴板文本，支持重试

    Returns:
        str: 剪贴板文本内容，失败返回 None
    """
    max_retries = 3
    retry_delay = 0.05  # 50ms

    for attempt in range(max_retries):
        try:
            clipboard = QApplication.clipboard()
            if clipboard:
                text = clipboard.text()
                return text if text else None
            return None
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    return None


def set_clipboard_text(text):
    """
    安全地设置剪贴板文本，支持重试

    Args:
        text (str): 要设置的文本内容

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    max_retries = 3
    retry_delay = 0.05  # 50ms

    for attempt in range(max_retries):
        try:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(text if text else '')
                return True
            return False
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    return False


def process_clipboard_text(text):
    """
    处理剪贴板文本，将多行文本分割成列表

    Args:
        text (str): 原始文本

    Returns:
        list: 处理后的文本列表
    """
    if not text:
        return []

    if '\n' in text or '\r' in text:
        lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        return [line.strip() for line in lines if line.strip()]
    else:
        return [text.strip()] if text.strip() else []
