"""
Скрипт для создания установщика ChatList с помощью Inno Setup.
Использует версию из version.py для обновления .iss файла и создания установщика.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# Импортируем версию
from version import __version__

def update_iss_file(iss_path, version):
    """Обновляет версию в .iss файле."""
    try:
        with open(iss_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Обновляем строки построчно для более точной замены
        updated_lines = []
        for line in lines:
            # Обновляем #define AppExeName
            if line.strip().startswith('#define AppExeName'):
                line = f'#define AppExeName "ChatList-v{version}.exe"\n'
            # Обновляем #define AppVersion
            elif line.strip().startswith('#define AppVersion'):
                line = f'#define AppVersion "{version}"\n'
            # Обновляем #define AppVersionUnderscores
            elif line.strip().startswith('#define AppVersionUnderscores'):
                line = f'#define AppVersionUnderscores "{version.replace(".", "_")}"\n'
            # OutputBaseFilename использует макрос {#AppVersion}, поэтому не требует замены
            
            updated_lines.append(line)
        
        with open(iss_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        print(f"✓ Обновлен файл {iss_path} с версией {version}")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении .iss файла: {e}")
        return False

def find_inno_setup_compiler():
    """Ищет путь к компилятору Inno Setup."""
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def build_installer():
    """Создает установщик с помощью Inno Setup."""
    project_dir = Path(__file__).parent
    iss_path = project_dir / "ChatList.iss"
    dist_dir = project_dir / "dist"
    exe_name = f"ChatList-v{__version__}.exe"
    exe_path = dist_dir / exe_name
    
    print(f"Версия приложения: {__version__}")
    print(f"Проект: {project_dir}")
    print()
    
    # Проверяем наличие exe файла
    if not exe_path.exists():
        print(f"Ошибка: файл {exe_path} не найден.")
        print("Сначала выполните сборку: pyinstaller MinimalApp.spec")
        return 1
    
    # Обновляем .iss файл с версией
    if not update_iss_file(iss_path, __version__):
        return 1
    
    # Ищем компилятор Inno Setup
    iscc_path = find_inno_setup_compiler()
    if not iscc_path:
        print("Ошибка: Inno Setup Compiler не найден.")
        print("Установите Inno Setup с https://jrsoftware.org/isdl.php")
        print("Или укажите путь к ISCC.exe вручную.")
        return 1
    
    print(f"Найден Inno Setup Compiler: {iscc_path}")
    print(f"Компиляция установщика из {iss_path}...")
    print()
    
    # Компилируем установщик
    try:
        result = subprocess.run(
            [iscc_path, str(iss_path)],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            installer_name = f"ChatList-Setup-v{__version__}.exe"
            installer_path = project_dir / "installer" / installer_name
            print()
            print("=" * 60)
            print("✓ Установщик успешно создан!")
            print(f"  Файл: {installer_path}")
            print("=" * 60)
            return 0
        else:
            print("Ошибка при компиляции установщика:")
            print(result.stdout)
            print(result.stderr)
            return 1
    except Exception as e:
        print(f"Ошибка при запуске компилятора: {e}")
        return 1

if __name__ == "__main__":
    exit(build_installer())
