"""
窗口管理模块 - macOS/跨平台版本
使用 pyobjc 访问 macOS 窗口 API
"""

import time
import platform

# 判断当前平台
IS_MACOS = platform.system() == 'Darwin'

# 尝试导入 macOS 专用模块
HAS_MACOS_API = False
if IS_MACOS:
    try:
        from AppKit import NSWorkspace, NSRunningApplication
        from AppKit import NSApplicationActivateIgnoringOtherApps
        HAS_MACOS_API = True
    except ImportError:
        pass


def get_foreground_window():
    """
    获取当前活动窗口/应用程序

    Returns:
        macOS: NSRunningApplication 对象
        其他平台: None
    """
    if not IS_MACOS:
        return None

    if not HAS_MACOS_API:
        return None

    try:
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        return active_app
    except Exception:
        return None


def set_foreground_window(app):
    """
    激活指定应用程序

    Args:
        app: NSRunningApplication 对象 (macOS)

    Returns:
        bool: 是否成功
    """
    if not IS_MACOS:
        return False

    if not HAS_MACOS_API or not app:
        return False

    try:
        # 激活应用程序
        app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
        return True
    except Exception:
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
        保存当前活动窗口/应用

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
        获取之前保存的窗口/应用

        Returns:
            macOS: NSRunningApplication 对象
        """
        return self.previous_window
