"""
数据模型层 - macOS/跨平台版本
处理数据的持久化存储和读取
"""

import json
import os
import platform
import subprocess
from pathlib import Path
from PyQt5.QtCore import QObject

# 判断当前平台
IS_MACOS = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'


class DataModel:
    """数据模型 - 处理持久化存储"""

    def __init__(self, data_dir=None):
        """
        初始化数据模型

        Args:
            data_dir: 数据目录路径（可选）
        """
        if data_dir is None:
            data_dir = self._get_default_data_dir()
        else:
            data_dir = Path(data_dir)

        self.data_dir = data_dir
        self.data_file = data_dir / 'clipboard_data.json'
        self.settings_file = data_dir / 'settings.json'

        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_default_data_dir(self):
        """
        获取默认数据目录

        Returns:
            Path: 数据目录路径
        """
        if IS_MACOS:
            # macOS: ~/Library/Application Support/ClipboardHelper
            return Path.home() / 'Library' / 'Application Support' / 'ClipboardHelper'
        elif IS_WINDOWS:
            # Windows: %APPDATA%/ClipboardHelper
            appdata_dir = os.getenv('APPDATA')
            if appdata_dir:
                return Path(appdata_dir) / 'ClipboardHelper'
            else:
                return Path.home() / '.clipboard_helper'
        else:
            # Linux: ~/.config/ClipboardHelper
            return Path.home() / '.config' / 'ClipboardHelper'

    def save_clipboard_data(self, data):
        """
        保存剪贴板数据

        Args:
            data: 数据列表

        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def load_clipboard_data(self):
        """
        加载剪贴板数据

        Returns:
            list: 数据列表，失败返回空列表
        """
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []

    def clear_clipboard_data(self):
        """
        清除剪贴板数据文件

        Returns:
            bool: 是否清除成功
        """
        try:
            if self.data_file.exists():
                self.data_file.unlink()
            return True
        except Exception:
            return False

    def save_settings(self, settings):
        """
        保存设置

        Args:
            settings: 设置字典

        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def load_settings(self):
        """
        加载设置

        Returns:
            dict: 设置字典，失败返回默认设置
        """
        default_settings = {
            'output_mode': 'comma',
            'theme': self.detect_system_theme(),
            'color_scheme': 'pure_blue'
        }

        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
            return default_settings
        except Exception:
            return default_settings

    @staticmethod
    def detect_system_theme():
        """
        检测系统主题

        Returns:
            str: 'light' 或 'dark'
        """
        if IS_MACOS:
            return DataModel._detect_macos_theme()
        elif IS_WINDOWS:
            return DataModel._detect_windows_theme()
        else:
            return 'light'  # Linux 默认浅色

    @staticmethod
    def _detect_macos_theme():
        """
        检测 macOS 系统主题

        Returns:
            str: 'light' 或 'dark'
        """
        try:
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True,
                text=True
            )
            # 如果返回 "Dark"，则为深色模式
            if result.returncode == 0 and 'Dark' in result.stdout:
                return 'dark'
            return 'light'
        except Exception:
            return 'light'

    @staticmethod
    def _detect_windows_theme():
        """
        检测 Windows 系统主题

        Returns:
            str: 'light' 或 'dark'
        """
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return 'light' if value == 1 else 'dark'
        except Exception:
            return 'light'  # 默认日间模式
