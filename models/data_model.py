"""
数据模型层
处理数据的持久化存储和读取
"""

import json
import winreg
import os
from pathlib import Path
from PyQt5.QtCore import QObject


class DataModel:
    """数据模型 - 处理持久化存储"""

    def __init__(self, data_dir=None):
        """
        初始化数据模型

        Args:
            data_dir: 数据目录路径（可选）
        """
        if data_dir is None:
            # 使用用户 AppData 目录，确保打包后也能正常读写
            appdata_dir = os.getenv('APPDATA')  # 获取 C:\Users\用户名\AppData\Roaming
            if appdata_dir:
                data_dir = Path(appdata_dir) / 'ClipboardHelper'
            else:
                # 如果获取不到 AppData，使用用户主目录
                data_dir = Path.home() / '.clipboard_helper'
        else:
            data_dir = Path(data_dir)

        self.data_dir = data_dir
        self.data_file = data_dir / 'clipboard_data.json'
        self.settings_file = data_dir / 'settings.json'

        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)

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
        检测 Windows 系统主题

        Returns:
            str: 'light' 或 'dark'
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return 'light' if value == 1 else 'dark'
        except Exception:
            return 'light'  # 默认日间模式
