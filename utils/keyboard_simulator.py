"""
键盘模拟模块 - macOS/跨平台版本
使用 pynput 进行键盘模拟
"""

import time
import platform
from pynput.keyboard import Key, Controller

# 创建键盘控制器
keyboard = Controller()

# 判断当前平台
IS_MACOS = platform.system() == 'Darwin'


def send_input_key(key, up=False):
    """
    发送按键事件

    Args:
        key: 按键（pynput Key 或字符）
        up (bool): True 表示释放按键，False 表示按下按键
    """
    try:
        if up:
            keyboard.release(key)
        else:
            keyboard.press(key)
    except Exception:
        pass


def simulate_paste():
    """
    模拟粘贴操作
    macOS: Cmd+V
    Windows/Linux: Ctrl+V

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 选择修饰键：macOS 用 Cmd，其他平台用 Ctrl
        modifier = Key.cmd if IS_MACOS else Key.ctrl

        # 先释放所有修饰键
        release_all_modifiers()
        time.sleep(0.05)

        # 模拟粘贴组合键
        keyboard.press(modifier)
        time.sleep(0.02)
        keyboard.press('v')
        time.sleep(0.02)
        keyboard.release('v')
        time.sleep(0.02)
        keyboard.release(modifier)

        return True
    except Exception:
        return False


def simulate_key_combo(*keys, hold_time=0.02):
    """
    模拟组合键操作（通用）

    Args:
        *keys: pynput Key 或字符列表
        hold_time (float): 按键保持时间（秒）

    Example:
        simulate_key_combo(Key.cmd, 'v')  # Cmd+V (macOS)
        simulate_key_combo(Key.ctrl, 'v')  # Ctrl+V (Windows/Linux)
        simulate_key_combo(Key.cmd, Key.shift, 'c')  # Cmd+Shift+C
    """
    try:
        # 按下所有键
        for key in keys:
            keyboard.press(key)
            time.sleep(hold_time)

        # 释放所有键（逆序）
        for key in reversed(keys):
            keyboard.release(key)
            time.sleep(hold_time)

        return True
    except Exception:
        return False


def release_all_modifiers():
    """释放所有修饰键"""
    modifiers = [Key.ctrl, Key.alt, Key.shift]

    # macOS 额外释放 Cmd 键
    if IS_MACOS:
        modifiers.append(Key.cmd)

    for key in modifiers:
        try:
            keyboard.release(key)
        except Exception:
            pass


# 兼容性别名（保持与原 Windows 版本的接口一致）
VK_CONTROL = Key.ctrl
VK_SHIFT = Key.shift
VK_MENU = Key.alt  # Alt 键
VK_V = 'v'

# macOS 专用
VK_COMMAND = Key.cmd if IS_MACOS else Key.ctrl
