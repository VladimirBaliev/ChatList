# -*- mode: python ; coding: utf-8 -*-

# Импортируем версию приложения
import sys
import os
# Определяем путь к директории со spec файлом
if 'SPECPATH' in globals():
    spec_dir = os.path.dirname(os.path.abspath(SPECPATH))
else:
    # Если SPECPATH не определен, используем текущую директорию
    spec_dir = os.path.dirname(os.path.abspath(__file__ if '__file__' in globals() else os.path.abspath('MinimalApp.spec')))

# Добавляем путь в sys.path
if spec_dir not in sys.path:
    sys.path.insert(0, spec_dir)

# Импортируем версию
try:
    from version import __version__
except ImportError:
    # Если импорт не удался, пытаемся прочитать версию напрямую
    version_file = os.path.join(spec_dir, 'version.py')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    __version__ = line.split('=')[1].strip().strip('"').strip("'")
                    break
    else:
        __version__ = "1.0.0"  # Версия по умолчанию

# Собираем список скрытых импортов
# PyQt5 автоматически обнаруживается через стандартные хуки PyInstaller
hiddenimports = [
    'version',
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.sip',
    'requests',
    'dotenv',
    'markdown',
    'sqlite3',
    'db',
    'models',
    'network',
    'export',
    'windows',
    'prompt_improver',
]

# Собираем данные для включения в сборку
datas = []
binaries = []

# Добавляем иконку, если она есть
if os.path.exists(os.path.join(spec_dir, 'app.ico')):
    datas.append(('app.ico', '.'))

# Пытаемся найти и добавить DLL Qt и плагины для PyQt5
try:
    import PyQt5
    pyqt5_path = os.path.dirname(PyQt5.__file__)
    
    # Добавляем плагины Qt
    qt_plugins_path = os.path.join(pyqt5_path, 'Qt5', 'plugins')
    if os.path.exists(qt_plugins_path):
        datas.append((qt_plugins_path, 'PyQt5/Qt5/plugins'))
    
    # Добавляем ВСЕ DLL из Qt5/bin в корень _internal для лучшей доступности
    qt_bin_path = os.path.join(pyqt5_path, 'Qt5', 'bin')
    if os.path.exists(qt_bin_path):
        import glob
        # Копируем все DLL из bin в корень _internal
        all_dlls = glob.glob(os.path.join(qt_bin_path, '*.dll'))
        for dll in all_dlls:
            binaries.append((dll, '.'))  # Копируем в корень _internal
        # DLL добавлены в сборку
except Exception as e:
    # Ошибка при добавлении DLL Qt (не критично)
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,  # Добавляем DLL Qt
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={'pyqt5': {'no_qt_plugins': False}},  # Отключаем автоматический поиск плагинов
    runtime_hooks=['pyi_rth_pyqt5_fix.py'],  # Добавляем наш runtime hook
    excludes=['PyQt6'],  # Исключаем PyQt6, используем только PyQt5
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Собираем в режиме onedir для правильной работы Qt DLL
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=f'ChatList-v{__version__}',  # Используем версию в имени файла
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Не показываем консоль в релизной версии
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',  # Иконка для exe файла
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=f'ChatList-v{__version__}',  # Имя папки
)
