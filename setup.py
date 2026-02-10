"""
py2app 打包配置文件
使用方法: python setup.py py2app
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('themes', ['themes/__init__.py', 'themes/theme_manager.py']),
    ('ui', ['ui/__init__.py']),
    ('ui/components', [
        'ui/components/__init__.py',
        'ui/components/clickable_label.py',
        'ui/components/gradient_header.py',
        'ui/components/capsule_widget.py',
        'ui/components/tray_menu.py',
        'ui/components/clipboard_delegate.py',
        'ui/components/floating_icon.py',
    ]),
    ('utils', [
        'utils/__init__.py',
        'utils/clipboard_listener.py',
        'utils/clipboard_utils.py',
        'utils/data_manager.py',
        'utils/keyboard_simulator.py',
        'utils/window_manager.py',
    ]),
    ('models', ['models/data_model.py']),
    ('services', ['services/clipboard_service.py']),
]

OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleName': '剪贴板助手',
        'CFBundleDisplayName': '剪贴板助手',
        'CFBundleIdentifier': 'com.clipboardhelper.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # 隐藏 Dock 图标（作为菜单栏应用运行）
        'NSHighResolutionCapable': True,  # 支持 Retina 显示屏
        'NSRequiresAquaSystemAppearance': False,  # 支持深色模式
    },
    'packages': [
        'PyQt5',
        'pynput',
    ],
    'includes': [
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
    ],
}

setup(
    name='剪贴板助手',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
