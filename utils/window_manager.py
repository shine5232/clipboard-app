"""
窗口管理模块
提供 Windows 窗口焦点管理功能
"""

import ctypes
import time


def get_foreground_window():
    """
    获取当前活动窗口的句柄

    Returns:
        int: 窗口句柄，失败返回 None
    """
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        return hwnd if hwnd else None
    except Exception as e:
        print(f"获取前台窗口失败: {e}")
        return None


def set_foreground_window(hwnd):
    """
    激活指定窗口

    Args:
        hwnd (int): 窗口句柄

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        if not hwnd:
            return False

        user32 = ctypes.windll.user32
        result = user32.SetForegroundWindow(hwnd)
        return bool(result)
    except Exception as e:
        print(f"激活窗口失败: {e}")
        return False


class WindowFocusManager:
    """
    窗口焦点管理器
    用于记录和恢复窗口焦点
    """

    def __init__(self):
        self.previous_window = None

    def save_current_window(self):
        """
        保存当前活动窗口

        Returns:
            bool: 成功返回 True，失败返回 False
        """
        self.previous_window = get_foreground_window()
        return bool(self.previous_window)

    def restore_previous_window(self, wait_time=0.1):
        """
        恢复之前保存的窗口焦点

        Args:
            wait_time (float): 等待时间（秒）

        Returns:
            bool: 成功返回 True，失败返回 False
        """
        if not self.previous_window:
            return False

        success = set_foreground_window(self.previous_window)

        if wait_time > 0:
            time.sleep(wait_time)

        return success

    def get_previous_window(self):
        """
        获取之前保存的窗口句柄

        Returns:
            int: 窗口句柄
        """
        return self.previous_window
