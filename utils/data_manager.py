"""
数据管理模块
提供 JSON 文件的读写和数据持久化功能
"""

import json
from pathlib import Path


class DataManager:
    """数据管理器"""

    @staticmethod
    def load_json(file_path, default=None):
        """
        加载 JSON 文件

        Args:
            file_path (Path or str): 文件路径
            default: 加载失败时的默认值

        Returns:
            加载的数据，失败返回 default
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return default

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载 JSON 文件失败 ({file_path}): {e}")
            return default

    @staticmethod
    def save_json(file_path, data, indent=2):
        """
        保存数据到 JSON 文件

        Args:
            file_path (Path or str): 文件路径
            data: 要保存的数据
            indent (int): 缩进空格数

        Returns:
            bool: 成功返回 True，失败返回 False
        """
        file_path = Path(file_path)

        try:
            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except Exception as e:
            print(f"保存 JSON 文件失败 ({file_path}): {e}")
            return False


class ClipboardDataManager(DataManager):
    """剪贴板数据管理器"""

    def __init__(self, data_dir=None):
        """
        初始化数据管理器

        Args:
            data_dir (Path or str): 数据目录路径，默认为 ./data
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / 'data'
        else:
            data_dir = Path(data_dir)

        self.data_dir = data_dir
        self.clipboard_file = data_dir / 'clipboard_data.json'
        self.settings_file = data_dir / 'settings.json'

    def load_clipboard_data(self):
        """
        加载剪贴板数据

        Returns:
            list: 剪贴板数据列表
        """
        data = self.load_json(self.clipboard_file, default=[])

        # 标准化数据格式
        from datetime import datetime
        normalized_data = []
        for item in data:
            if isinstance(item, str):
                normalized_data.append({
                    'text': item,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            else:
                normalized_data.append(item)

        return normalized_data

    def save_clipboard_data(self, data):
        """
        保存剪贴板数据

        Args:
            data (list): 剪贴板数据列表

        Returns:
            bool: 成功返回 True，失败返回 False
        """
        return self.save_json(self.clipboard_file, data)

    def load_settings(self, default_settings=None):
        """
        加载设置

        Args:
            default_settings (dict): 默认设置

        Returns:
            dict: 设置字典
        """
        if default_settings is None:
            default_settings = {
                'output_mode': 'comma',
                'theme': 'light',
                'color_scheme': 'pure_blue'
            }

        loaded_settings = self.load_json(self.settings_file, default={})

        # 合并默认设置和加载的设置
        settings = default_settings.copy()
        settings.update(loaded_settings)

        return settings

    def save_settings(self, settings):
        """
        保存设置

        Args:
            settings (dict): 设置字典

        Returns:
            bool: 成功返回 True，失败返回 False
        """
        return self.save_json(self.settings_file, settings)
