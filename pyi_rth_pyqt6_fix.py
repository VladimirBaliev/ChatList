"""
Runtime hook для исправления путей к DLL PyQt6.
Добавляет путь к DLL Qt в PATH перед импортом PyQt6.
"""
import os
import sys

# Если программа запущена как exe (frozen)
if getattr(sys, 'frozen', False):
    # Путь к директории с exe
    if hasattr(sys, '_MEIPASS'):
        # Режим onefile - временная директория
        base_path = sys._MEIPASS
    else:
        # Режим onedir - директория с exe
        base_path = os.path.dirname(sys.executable)
    
    # Список путей для добавления в PATH
    paths_to_add = []
    
    # 1. Корень _internal (куда мы копируем DLL)
    internal_path = os.path.join(base_path, '_internal')
    if os.path.exists(internal_path):
        paths_to_add.append(internal_path)
    
    # 2. PyQt6/Qt6/bin (оригинальный путь)
    qt_bin_path = os.path.join(base_path, '_internal', 'PyQt6', 'Qt6', 'bin')
    if os.path.exists(qt_bin_path):
        paths_to_add.append(qt_bin_path)
    
    # Обновляем PATH
    if paths_to_add:
        new_path = os.pathsep.join(paths_to_add) + os.pathsep + os.environ.get('PATH', '')
        os.environ['PATH'] = new_path
        
        # Также добавляем через AddDllDirectory для Windows
        if sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import wintypes
                kernel32 = ctypes.windll.kernel32
                
                # Правильный способ вызова AddDllDirectory
                if hasattr(kernel32, 'AddDllDirectory'):
                    AddDllDirectory = kernel32.AddDllDirectory
                    AddDllDirectory.argtypes = [wintypes.LPCWSTR]
                    AddDllDirectory.restype = wintypes.HANDLE
                    
                    for path in paths_to_add:
                        try:
                            handle = AddDllDirectory(path)
                            if not handle:
                                # Если не получилось, пробуем альтернативный способ
                                try:
                                    kernel32.AddDllDirectoryW(path)
                                except:
                                    pass
                        except:
                            pass
            except:
                # Если AddDllDirectory не доступен, просто используем PATH
                pass
