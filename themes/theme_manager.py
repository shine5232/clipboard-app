"""
主题管理模块
提供统一的主题和样式管理
"""


class ThemeManager:
    """主题管理器"""

    # 配色方案定义
    COLOR_SCHEMES = {
        'blue_gradient': {
            'light': ('#667eea', '#764ba2'),
            'dark': ('#4a5568', '#2d3748')
        },
        'pure_blue': {
            'light': ('#7ba3d6', '#7ba3d6'),
            'dark': ('#5a7a9c', '#5a7a9c')
        },
        'pure_green': {
            'light': ('#7fb896', '#7fb896'),
            'dark': ('#5a8c6e', '#5a8c6e')
        }
    }

    def __init__(self, theme='light', color_scheme='pure_blue'):
        """
        初始化主题管理器

        Args:
            theme (str): 主题名称 ('light' 或 'dark')
            color_scheme (str): 配色方案名称
        """
        self.theme = theme
        self.color_scheme = color_scheme

    @property
    def is_dark(self):
        """是否为暗夜模式"""
        return self.theme == 'dark'

    def set_theme(self, theme):
        """设置主题"""
        self.theme = theme

    def set_color_scheme(self, color_scheme):
        """设置配色方案"""
        self.color_scheme = color_scheme

    def get_colors(self):
        """
        获取当前配色方案的颜色

        Returns:
            tuple: (color1, color2) 用于渐变或纯色
        """
        scheme = self.COLOR_SCHEMES.get(self.color_scheme, self.COLOR_SCHEMES['pure_blue'])
        mode = 'dark' if self.is_dark else 'light'
        return scheme[mode]

    def get_gradient_style(self):
        """获取渐变样式字符串"""
        color1, color2 = self.get_colors()
        return f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:1 {color2})"

    # ==================== 组件样式 ====================

    def get_label_style(self, font_size=13):
        """
        获取标签样式

        Args:
            font_size (int): 字体大小

        Returns:
            str: CSS 样式字符串
        """
        if self.is_dark:
            return f"""
                QLabel {{
                    background: transparent;
                    border: none;
                    color: #e0e0e0;
                    font-size: {font_size}px;
                }}
            """
        else:
            return f"""
                QLabel {{
                    background: transparent;
                    border: none;
                    color: #303133;
                    font-size: {font_size}px;
                }}
            """

    def get_time_label_style(self):
        """获取时间标签样式"""
        if self.is_dark:
            return """
                QLabel {
                    background: transparent;
                    border: none;
                    color: #888888;
                    font-size: 12px;
                }
            """
        else:
            return """
                QLabel {
                    background: transparent;
                    border: none;
                    color: #909399;
                    font-size: 12px;
                }
            """

    def get_list_item_style(self):
        """获取列表项样式"""
        if self.is_dark:
            return """
                QWidget {
                    background: #2d2d2d;
                    border: none;
                    border-radius: 6px;
                }
                QWidget:hover {
                    background: #3d3d3d;
                }
            """
        else:
            return """
                QWidget {
                    background: #f5f7fa;
                    border: none;
                    border-radius: 6px;
                }
                QWidget:hover {
                    background: #e8edf5;
                }
            """

    def get_delete_button_style(self):
        """获取删除按钮样式"""
        return """
            QPushButton {
                background: #f56c6c;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #f34040;
            }
        """

    def get_primary_button_style(self):
        """获取主要按钮样式"""
        color1, color2 = self.get_colors()
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2});
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color1}, stop:1 {color2});
                opacity: 0.9;
            }}
        """

    def get_secondary_button_style(self):
        """获取次要按钮样式"""
        if self.is_dark:
            return """
                QPushButton {
                    background: #3d3d3d;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #4d4d4d;
                    border-color: #666666;
                }
            """
        else:
            return """
                QPushButton {
                    background: #f5f7fa;
                    color: #606266;
                    border: 1px solid #dcdfe6;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #e8edf5;
                    border-color: #c0c4cc;
                }
            """

    def get_combo_box_style(self):
        """获取下拉框样式"""
        color1, color2 = self.get_colors()

        if self.is_dark:
            return f"""
                #settingCombo {{
                    background: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #444444;
                    border-radius: 6px;
                    padding: 6px 10px;
                    padding-right: 25px;
                    font-size: 13px;
                }}
                #settingCombo:hover {{
                    border-color: #5a6678;
                }}
                #settingCombo::drop-down {{
                    border: none;
                    width: 20px;
                    subcontrol-position: right center;
                    subcontrol-origin: padding;
                    right: 5px;
                }}
                #settingCombo QAbstractItemView {{
                    background: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #444444;
                    border-radius: 8px;
                    padding: 6px;
                    outline: none;
                    selection-background-color: transparent;
                }}
                #settingCombo QAbstractItemView::item {{
                    height: 36px;
                    padding: 8px 12px;
                    margin: 3px 4px;
                    border-radius: 6px;
                    background: transparent;
                    color: #e0e0e0;
                }}
                #settingCombo QAbstractItemView::item:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(90, 122, 156, 0.4), stop:1 rgba(90, 122, 156, 0.4));
                }}
                #settingCombo QAbstractItemView::item:selected {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color1}, stop:1 {color2});
                    color: white;
                }}
            """
        else:
            return f"""
                #settingCombo {{
                    background: #f5f7fa;
                    color: #303133;
                    border: 1px solid #dcdfe6;
                    border-radius: 6px;
                    padding: 6px 10px;
                    padding-right: 25px;
                    font-size: 13px;
                }}
                #settingCombo:hover {{
                    border-color: {color1};
                }}
                #settingCombo::drop-down {{
                    border: none;
                    width: 20px;
                    subcontrol-position: right center;
                    subcontrol-origin: padding;
                    right: 5px;
                }}
                #settingCombo QAbstractItemView {{
                    background: #ffffff;
                    color: #303133;
                    border: 1px solid rgba(102, 126, 234, 0.3);
                    border-radius: 8px;
                    padding: 6px;
                    outline: none;
                    selection-background-color: transparent;
                }}
                #settingCombo QAbstractItemView::item {{
                    height: 36px;
                    padding: 8px 12px;
                    margin: 3px 4px;
                    border-radius: 6px;
                    background: transparent;
                    color: #303133;
                }}
                #settingCombo QAbstractItemView::item:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(123, 163, 214, 0.15), stop:1 rgba(123, 163, 214, 0.15));
                }}
                #settingCombo QAbstractItemView::item:selected {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color1}, stop:1 {color2});
                    color: white;
                }}
            """

    def get_list_widget_style(self):
        """获取列表控件样式"""
        if self.is_dark:
            return """
                QListWidget {
                    background: transparent;
                    border: none;
                    padding: 8px;
                    font-size: 14px;
                }
                QListWidget::item {
                    background: transparent;
                    border: none;
                    padding: 0px;
                }
                QListWidget::item:disabled {
                    background: transparent;
                    color: #888888;
                    border: none;
                }
                QListWidget::item:hover {
                    background: transparent;
                }
                QListWidget::item:selected {
                    background: transparent;
                }
                QScrollBar:vertical {
                    background: transparent;
                    width: 8px;
                    margin: 0px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(102, 126, 234, 0.5),
                        stop:1 rgba(118, 75, 162, 0.5));
                    min-height: 30px;
                    border-radius: 4px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(102, 126, 234, 0.8),
                        stop:1 rgba(118, 75, 162, 0.8));
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
            """
        else:
            return """
                QListWidget {
                    background: transparent;
                    border: none;
                    padding: 8px;
                    font-size: 14px;
                }
                QListWidget::item {
                    background: transparent;
                    border: none;
                    padding: 0px;
                }
                QListWidget::item:disabled {
                    background: transparent;
                    color: #909399;
                    border: none;
                }
                QListWidget::item:hover {
                    background: transparent;
                }
                QListWidget::item:selected {
                    background: transparent;
                }
                QScrollBar:vertical {
                    background: transparent;
                    width: 8px;
                    margin: 0px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(102, 126, 234, 0.3),
                        stop:1 rgba(118, 75, 162, 0.3));
                    min-height: 30px;
                    border-radius: 4px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(102, 126, 234, 0.6),
                        stop:1 rgba(118, 75, 162, 0.6));
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
            """

    def get_container_style(self):
        """获取容器样式"""
        if self.is_dark:
            return """
                QWidget {
                    background: #1e1e1e;
                    border: 1px solid rgba(102, 126, 234, 0.3);
                    border-radius: 10px;
                }
            """
        else:
            return """
                QWidget {
                    background: #ffffff;
                    border: 1px solid rgba(102, 126, 234, 0.3);
                    border-radius: 10px;
                }
            """

    def get_setting_title_style(self):
        """获取设置标题样式"""
        if self.is_dark:
            return """
                QLabel {
                    color: #e0e0e0;
                    font-size: 14px;
                    font-weight: 500;
                }
            """
        else:
            return """
                QLabel {
                    color: #303133;
                    font-size: 14px;
                    font-weight: 500;
                }
            """

    def get_setting_desc_style(self):
        """获取设置描述样式"""
        if self.is_dark:
            return """
                QLabel {
                    color: #888888;
                    font-size: 12px;
                }
            """
        else:
            return """
                QLabel {
                    color: #909399;
                    font-size: 12px;
                }
            """


# 向后兼容的全局函数
def get_color_scheme_colors(scheme, is_dark=False):
    """
    获取配色方案的颜色（向后兼容）

    Args:
        scheme (str): 配色方案名称
        is_dark (bool): 是否为暗夜模式

    Returns:
        tuple: (color1, color2)
    """
    theme = 'dark' if is_dark else 'light'
    manager = ThemeManager(theme=theme, color_scheme=scheme)
    return manager.get_colors()
