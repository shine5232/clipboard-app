"""
剪贴板业务逻辑服务
处理剪贴板数据的核心业务逻辑
"""

import time
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from utils.clipboard_utils import get_clipboard_text, set_clipboard_text, process_clipboard_text
from utils.keyboard_simulator import simulate_paste
from utils.window_manager import get_foreground_window, set_foreground_window


class ClipboardService(QObject):
    """剪贴板服务 - 处理核心业务逻辑"""

    # 信号
    data_changed = pyqtSignal()  # 数据变化信号
    notification_requested = pyqtSignal(str)  # 请求显示通知

    def __init__(self):
        super().__init__()

        # 数据存储
        self.clipboard_data = []

        # 输出模式
        self.output_mode = 'comma'  # 'comma', 'sequential', 'reverse'

        # 状态管理
        self.last_pasted_text = ""
        self.last_paste_time = 0
        self.paste_ignore_until = 0
        self.sequential_index = -1
        self.previous_window = None
        self.last_clipboard_text = ""

    def get_data_count(self):
        """获取数据条数"""
        return len(self.clipboard_data)

    def get_all_data(self):
        """获取所有数据"""
        return self.clipboard_data.copy()

    def set_output_mode(self, mode):
        """设置输出模式"""
        if mode in ['comma', 'sequential', 'reverse']:
            self.output_mode = mode
            self.sequential_index = -1  # 重置索引

    def get_output_mode(self):
        """获取输出模式"""
        return self.output_mode

    def add_clipboard_item(self, text, timestamp=None, silent=False):
        """
        添加剪贴板项

        Args:
            text: 文本内容
            timestamp: 时间戳（可选）
            silent: 是否静默添加（不发送通知）

        Returns:
            int: 添加的条数
        """
        if not text:
            return 0

        # 处理文本（分割多行）
        texts = process_clipboard_text(text)

        added_count = 0
        for text_item in texts:
            # 检查是否已存在
            if not any(item['text'] == text_item for item in self.clipboard_data):
                self.clipboard_data.append({
                    'text': text_item,
                    'timestamp': timestamp or datetime.now().strftime('%H:%M:%S')
                })
                added_count += 1

        if added_count > 0:
            self.sequential_index = -1  # 重置顺序输出索引
            self.data_changed.emit()

            # 发送通知
            if not silent:
                if added_count == 1:
                    msg = f'已复制: {texts[0][:20]}...' if len(texts[0]) > 20 else f'已复制: {texts[0]}'
                else:
                    msg = f'已添加 {added_count} 项'
                self.notification_requested.emit(msg)

        return added_count

    def remove_item_by_text(self, text):
        """
        删除指定文本的项

        Args:
            text: 要删除的文本

        Returns:
            bool: 是否删除成功
        """
        original_length = len(self.clipboard_data)
        self.clipboard_data = [
            item for item in self.clipboard_data
            if (item['text'] if isinstance(item, dict) else item) != text
        ]

        if len(self.clipboard_data) < original_length:
            self.data_changed.emit()
            return True
        return False

    def clear_all(self):
        """清空所有数据"""
        if not self.clipboard_data:
            return False

        self.clipboard_data.clear()
        self.sequential_index = -1
        self.data_changed.emit()

        # 清空系统剪贴板
        set_clipboard_text('')
        self.last_clipboard_text = ''
        return True

    def should_ignore_clipboard_change(self, current_text):
        """
        判断是否应该忽略剪贴板变化

        Args:
            current_text: 当前剪贴板文本

        Returns:
            bool: 是否应该忽略
        """
        current_time = time.time()

        # 如果在忽略时间内，跳过
        if current_time < self.paste_ignore_until:
            return True

        # 检查是否是我们刚粘贴的内容
        if current_text == self.last_pasted_text and current_time < self.last_paste_time + 3.0:
            return True

        return False

    def handle_clipboard_change(self, new_text, is_window_visible=False):
        """
        处理剪贴板变化

        Args:
            new_text: 新的剪贴板文本
            is_window_visible: 窗口是否可见

        Returns:
            int: 添加的条数
        """
        if not new_text:
            return 0

        # 只在窗口隐藏时发送通知
        return self.add_clipboard_item(new_text, silent=is_window_visible)

    def prepare_paste_content(self):
        """
        准备粘贴内容

        Returns:
            tuple: (要粘贴的文本, 是否成功准备)
        """
        if not self.clipboard_data:
            return None, False

        text_to_paste = None

        if self.output_mode == 'sequential':
            # 顺序输出：先进先出（FIFO）
            if self.sequential_index < 0 or self.sequential_index >= len(self.clipboard_data):
                self.sequential_index = 0

            current_item = self.clipboard_data[self.sequential_index]
            text_to_paste = current_item['text'] if isinstance(current_item, dict) else current_item

        elif self.output_mode == 'reverse':
            # 倒序输出：后进先出（LIFO）
            if self.sequential_index < 0 or self.sequential_index >= len(self.clipboard_data):
                self.sequential_index = len(self.clipboard_data) - 1

            current_item = self.clipboard_data[self.sequential_index]
            text_to_paste = current_item['text'] if isinstance(current_item, dict) else current_item

        else:
            # 逗号拼接模式
            texts = [item['text'] if isinstance(item, dict) else item for item in self.clipboard_data]
            text_to_paste = ','.join(texts)

        if text_to_paste:
            # 记录粘贴信息
            self.last_pasted_text = text_to_paste
            self.last_paste_time = time.time()
            self.paste_ignore_until = time.time() + 1.5

            # 设置剪贴板
            if set_clipboard_text(text_to_paste):
                self.last_clipboard_text = text_to_paste
                return text_to_paste, True

        return None, False

    def update_sequential_index(self):
        """更新顺序输出索引（在粘贴完成后调用）"""
        if self.output_mode == 'sequential':
            self.sequential_index += 1
            if self.sequential_index >= len(self.clipboard_data):
                self.sequential_index = 0
        elif self.output_mode == 'reverse':
            self.sequential_index -= 1
            if self.sequential_index < 0:
                self.sequential_index = len(self.clipboard_data) - 1

    def prepare_single_paste(self, text):
        """
        准备单项粘贴

        Args:
            text: 要粘贴的文本

        Returns:
            bool: 是否成功准备
        """
        if not text:
            return False

        # 记录粘贴信息
        self.last_pasted_text = text
        self.last_paste_time = time.time()
        self.paste_ignore_until = time.time() + 1.5

        # 设置剪贴板
        if set_clipboard_text(text):
            self.last_clipboard_text = text
            return True

        return False

    def execute_paste(self):
        """执行粘贴操作"""
        simulate_paste()

    def save_previous_window(self):
        """保存当前活动窗口"""
        self.previous_window = get_foreground_window()

    def restore_previous_window(self):
        """恢复前一个窗口"""
        if self.previous_window:
            set_foreground_window(self.previous_window)
            time.sleep(0.1)

    def load_data(self, data):
        """
        加载数据

        Args:
            data: 数据列表
        """
        self.clipboard_data = []
        for item in data:
            if isinstance(item, str):
                self.clipboard_data.append({
                    'text': item,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            else:
                self.clipboard_data.append(item)
        self.data_changed.emit()

    def get_data_for_save(self):
        """获取用于保存的数据"""
        return self.clipboard_data.copy()
