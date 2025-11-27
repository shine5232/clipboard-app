"""
键盘模拟模块
使用 Windows SendInput API 模拟键盘输入
"""

import time
import ctypes
from ctypes import wintypes


# Windows API 常量
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

# 虚拟键码
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12  # Alt
VK_V = 0x56


class KEYBDINPUT(ctypes.Structure):
    """键盘输入结构体"""
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class MOUSEINPUT(ctypes.Structure):
    """鼠标输入结构体"""
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class HARDWAREINPUT(ctypes.Structure):
    """硬件输入结构体"""
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]


class INPUT_UNION(ctypes.Union):
    """输入联合体"""
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT)
    ]


class INPUT(ctypes.Structure):
    """输入结构体"""
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION)
    ]


def send_input_key(vk, up=False):
    """
    使用 SendInput 发送按键

    Args:
        vk (int): 虚拟键码
        up (bool): True 表示释放按键，False 表示按下按键
    """
    extra = ctypes.c_ulong(0)
    flags = KEYEVENTF_KEYUP if up else 0

    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = 0
    inp.union.ki.dwFlags = flags
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = ctypes.pointer(extra)

    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def simulate_paste():
    """
    模拟 Ctrl+V 粘贴操作

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 先释放所有修饰键（Ctrl、Alt、Shift）
        send_input_key(VK_CONTROL, up=True)
        send_input_key(VK_MENU, up=True)
        send_input_key(VK_SHIFT, up=True)
        time.sleep(0.05)

        # 模拟 Ctrl+V
        send_input_key(VK_CONTROL, up=False)
        time.sleep(0.02)
        send_input_key(VK_V, up=False)
        time.sleep(0.02)
        send_input_key(VK_V, up=True)
        time.sleep(0.02)
        send_input_key(VK_CONTROL, up=True)
        return True
    except Exception:
        return False


def simulate_key_combo(*keys, hold_time=0.02):
    """
    模拟组合键操作（通用）

    Args:
        *keys: 虚拟键码列表
        hold_time (float): 按键保持时间（秒）

    Example:
        simulate_key_combo(VK_CONTROL, VK_V)  # Ctrl+V
        simulate_key_combo(VK_CONTROL, VK_SHIFT, ord('C'))  # Ctrl+Shift+C
    """
    try:
        # 按下所有键
        for vk in keys:
            send_input_key(vk, up=False)
            time.sleep(hold_time)

        # 释放所有键（逆序）
        for vk in reversed(keys):
            send_input_key(vk, up=True)
            time.sleep(hold_time)

        return True
    except Exception:
        return False


def release_all_modifiers():
    """释放所有修饰键"""
    send_input_key(VK_CONTROL, up=True)
    send_input_key(VK_MENU, up=True)
    send_input_key(VK_SHIFT, up=True)
