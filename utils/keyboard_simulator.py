"""
键盘模拟模块 - macOS 版本
使用 pynput 进行键盘模拟
"""

import time
from pynput.keyboard import Key, Controller

# 创建键盘控制器
keyboard = Controller()


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
    模拟粘贴操作 (Cmd+V)

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 先释放所有修饰键
        release_all_modifiers()
        time.sleep(0.05)

        # 模拟 Cmd+V
        keyboard.press(Key.cmd)
        time.sleep(0.02)
        keyboard.press('v')
        time.sleep(0.02)
        keyboard.release('v')
        time.sleep(0.02)
        keyboard.release(Key.cmd)

        return True
    except Exception:
        return False


def simulate_key_combo(*keys, hold_time=0.02):
    """
    模拟组合键操作

    Args:
        *keys: pynput Key 或字符列表
        hold_time (float): 按键保持时间（秒）

    Example:
        simulate_key_combo(Key.cmd, 'v')  # Cmd+V
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
    modifiers = [Key.ctrl, Key.alt, Key.shift, Key.cmd]
    for key in modifiers:
        try:
            keyboard.release(key)
        except Exception:
            pass


# 兼容性别名
VK_CONTROL = Key.ctrl
VK_SHIFT = Key.shift
VK_MENU = Key.alt  # Alt 键
VK_V = 'v'
VK_COMMAND = Key.cmd
