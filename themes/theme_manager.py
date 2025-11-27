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
        },
        'sakura_pink': {
            'light': ('#ff6b9d', '#ff6b9d'),
            'dark': ('#d5578a', '#d5578a')
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

    def get_primary_button_style(self, selector='QPushButton'):
        """
        获取主要按钮样式

        Args:
            selector: CSS选择器，默认为 'QPushButton'，可以传入如 '#applyBtn, #okBtn'
        """
        color1, color2 = self.get_colors()

        # 计算悬停和按下时的深色
        from PyQt5.QtGui import QColor
        c1 = QColor(color1)
        c2 = QColor(color2)

        # 悬停时稍微变亮
        hover_c1 = c1.lighter(115).name()
        hover_c2 = c2.lighter(115).name()

        # 按下时稍微变暗
        press_c1 = c1.darker(110).name()
        press_c2 = c2.darker(110).name()

        # 处理多选择器的情况，为每个选择器添加伪类
        def add_pseudo_class(selectors, pseudo):
            """为每个选择器添加伪类"""
            parts = [s.strip() for s in selectors.split(',')]
            return ', '.join([f'{s}{pseudo}' for s in parts])

        hover_selector = add_pseudo_class(selector, ':hover')
        pressed_selector = add_pseudo_class(selector, ':pressed')

        return f"""
            {selector} {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2});
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            {hover_selector} {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {hover_c1}, stop:1 {hover_c2});
            }}
            {pressed_selector} {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {press_c1}, stop:1 {press_c2});
            }}
        """

    def get_secondary_button_style(self, selector='QPushButton'):
        """
        获取次要按钮样式

        Args:
            selector: CSS选择器，默认为 'QPushButton'，可以传入如 '#cancelBtn'
        """
        # 处理多选择器的情况，为每个选择器添加伪类
        def add_pseudo_class(selectors, pseudo):
            """为每个选择器添加伪类"""
            parts = [s.strip() for s in selectors.split(',')]
            return ', '.join([f'{s}{pseudo}' for s in parts])

        hover_selector = add_pseudo_class(selector, ':hover')
        pressed_selector = add_pseudo_class(selector, ':pressed')

        if self.is_dark:
            return f"""
                {selector} {{
                    background: #3d3d3d;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    font-size: 13px;
                }}
                {hover_selector} {{
                    background: #4d4d4d;
                    border-color: #666666;
                }}
                {pressed_selector} {{
                    background: #2d2d2d;
                    border-color: #444444;
                }}
            """
        else:
            return f"""
                {selector} {{
                    background: #f5f7fa;
                    color: #606266;
                    border: 1px solid #dcdfe6;
                    border-radius: 6px;
                    font-size: 13px;
                }}
                {hover_selector} {{
                    background: #e8edf5;
                    border-color: #c0c4cc;
                }}
                {pressed_selector} {{
                    background: #d8dde5;
                    border-color: #a0a4ac;
                }}
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
        """获取列表控件样式 - 完全隐藏滚动条"""
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
                    width: 0px;
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
                    width: 0px;
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

    def get_header_button_style(self):
        """获取头部按钮样式（透明背景）"""
        return """
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.35);
            }
        """

    def get_header_close_button_style(self):
        """获取头部关闭按钮样式"""
        return """
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 100, 100, 0.8);
            }
        """

    def get_header_icon_button_style(self):
        """获取头部图标按钮样式（用于设置、清空等）"""
        return """
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.35);
            }
        """

    def get_header_mode_label_style(self):
        """获取模式标识标签样式"""
        return """
            QLabel {
                background: rgba(255, 255, 255, 0.25);
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """

    def get_header_clear_button_style(self):
        """获取清空按钮样式"""
        return """
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 100, 100, 0.6);
            }
        """

    def get_header_label_style(self):
        """获取头部标签样式"""
        return """
            QLabel {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 600;
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
