"""
剪贴板工具模块
提供剪贴板读写和文本处理功能
"""

import time
import win32clipboard
import win32con


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
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    return data
            finally:
                win32clipboard.CloseClipboard()
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
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            finally:
                win32clipboard.CloseClipboard()
            return True
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
