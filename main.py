"""
Главный модуль приложения ChatList.
Содержит основной интерфейс пользователя.
"""
import sys
import os
import traceback
import time

# Определяем путь к лог файлу СРАЗУ, используя несколько вариантов
log_file = None
application_path = None

try:
    if getattr(sys, 'frozen', False):
        # Если программа запущена как exe
        application_path = os.path.dirname(sys.executable)
        # Для Program Files используем пользовательскую директорию для логов
        if 'Program Files' in application_path:
            import os
            user_data_dir = os.path.join(os.environ.get('APPDATA', ''), 'ChatList')
            try:
                os.makedirs(user_data_dir, exist_ok=True)
                log_file = os.path.join(user_data_dir, 'chatlist.log')
            except:
                # Если не удалось, используем временную директорию
                import tempfile
                log_file = os.path.join(tempfile.gettempdir(), 'chatlist.log')
        else:
            log_file = os.path.join(application_path, 'chatlist.log')
    else:
        # Если программа запущена как скрипт
        application_path = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(application_path, 'chatlist.log')
except:
    # Если не удалось определить путь, используем временную директорию
    try:
        import tempfile
        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, 'chatlist.log')
        application_path = temp_dir
    except:
        # Последний вариант - текущая директория
        log_file = 'chatlist.log'
        application_path = os.getcwd()

def write_log(message):
    """Записывает сообщение в лог файл с немедленным сохранением."""
    global log_file
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            f.flush()
            try:
                os.fsync(f.fileno())  # Принудительная запись на диск
            except:
                pass
    except Exception as e:
        # Если не удалось записать в файл, выводим в stderr
        print(f"Не удалось записать в лог: {e}", file=sys.stderr)
        print(f"Сообщение: {message}", file=sys.stderr)
        print(f"Путь к лог файлу: {log_file}", file=sys.stderr)

def log_error(message, exc_info=None):
    """Записывает ошибку в лог файл."""
    write_log(f"ERROR: {message}")
    if exc_info:
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(traceback.format_exc() + "\n")
                f.flush()
                try:
                    os.fsync(f.fileno())
                except:
                    pass
        except:
            pass
    traceback.print_exc()

# Инициализируем лог файл СРАЗУ
try:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== Запуск ChatList ===\n")
        f.write(f"Python версия: {sys.version}\n")
        f.write(f"Путь к приложению: {application_path}\n")
        f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(f"Путь к лог файлу: {log_file}\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except:
            pass
    write_log("Лог файл инициализирован")
except Exception as e:
    # Выводим в stderr и пытаемся создать в другом месте
    print(f"Не удалось создать лог файл в {log_file}: {e}", file=sys.stderr)
    try:
        import tempfile
        log_file = os.path.join(tempfile.gettempdir(), 'chatlist.log')
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Запуск ChatList (временный лог) ===\n")
            f.write(f"Оригинальный путь не доступен\n")
            f.write(f"Python версия: {sys.version}\n")
            f.flush()
        print(f"Лог файл создан в: {log_file}", file=sys.stderr)
    except:
        print("Не удалось создать лог файл ни в одном месте!", file=sys.stderr)

# Устанавливаем рабочую директорию на директорию скрипта
write_log("Настройка путей...")
if getattr(sys, 'frozen', False):
    # Если программа запущена как exe
    application_path = os.path.dirname(sys.executable)
    write_log(f"Режим exe, путь: {application_path}")
    # В режиме onedir DLL находятся в _internal/PyQt5/Qt5/bin
    # Также пробуем корень _internal, куда мы копируем DLL
    qt_bin_path = os.path.join(application_path, '_internal', 'PyQt5', 'Qt5', 'bin')
    qt_internal_path = os.path.join(application_path, '_internal')
    
    write_log(f"Путь к DLL Qt (bin): {qt_bin_path}, существует: {os.path.exists(qt_bin_path)}")
    write_log(f"Путь к _internal: {qt_internal_path}, существует: {os.path.exists(qt_internal_path)}")
    
    # Добавляем оба пути в PATH
    paths_to_add = []
    if os.path.exists(qt_bin_path):
        paths_to_add.append(qt_bin_path)
    if os.path.exists(qt_internal_path):
        paths_to_add.append(qt_internal_path)
    
    if paths_to_add:
        new_path = os.pathsep.join(paths_to_add) + os.pathsep + os.environ.get('PATH', '')
        os.environ['PATH'] = new_path
        write_log(f"PATH обновлен, добавлены пути: {paths_to_add}")
        
        # Проверяем наличие основных DLL Qt
        import glob
        for path in paths_to_add:
            qt_core_dll = os.path.join(path, 'Qt5Core.dll')
            if os.path.exists(qt_core_dll):
                write_log(f"Найден Qt5Core.dll в: {qt_core_dll}")
                # Проверяем размер файла
                try:
                    size = os.path.getsize(qt_core_dll)
                    write_log(f"Размер Qt5Core.dll: {size} байт")
                except:
                    pass
            else:
                write_log(f"Qt5Core.dll НЕ найден в: {path}")
                # Ищем все DLL Qt в этой папке
                qt_dlls = glob.glob(os.path.join(path, 'Qt5*.dll'))
                write_log(f"Найдено DLL Qt в {path}: {len(qt_dlls)} файлов")
                if qt_dlls:
                    write_log(f"Примеры: {[os.path.basename(d) for d in qt_dlls[:5]]}")
        
        # Также добавляем через AddDllDirectory для Windows
        if sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import wintypes
                kernel32 = ctypes.windll.kernel32
                # Правильный способ вызова AddDllDirectoryW
                AddDllDirectory = kernel32.AddDllDirectory
                AddDllDirectory.argtypes = [wintypes.LPCWSTR]
                AddDllDirectory.restype = wintypes.HANDLE
                
                for path in paths_to_add:
                    handle = AddDllDirectory(path)
                    if handle:
                        write_log(f"AddDllDirectory успешно для {path}, handle: {handle}")
                    else:
                        error = ctypes.get_last_error()
                        write_log(f"AddDllDirectory вернул NULL для {path}, ошибка: {error}")
            except Exception as e:
                write_log(f"Ошибка AddDllDirectory: {e}")
                # Пробуем альтернативный способ
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    for path in paths_to_add:
                        result = kernel32.AddDllDirectoryW(path)
                        write_log(f"AddDllDirectoryW (альтернативный способ) для {path}, результат: {result}")
                except Exception as e2:
                    write_log(f"Альтернативный способ тоже не сработал: {e2}")
else:
    # Если программа запущена как скрипт
    application_path = os.path.dirname(os.path.abspath(__file__))
    write_log(f"Режим скрипт, путь: {application_path}")

try:
    os.chdir(application_path)
    write_log(f"Рабочая директория установлена: {os.getcwd()}")
except Exception as e:
    write_log(f"Ошибка установки рабочей директории: {e}")

# Настраиваем путь к плагинам Qt для PyQt5
try:
    import PyQt5
    pyqt5_path = os.path.dirname(PyQt5.__file__)
    plugins_path = os.path.join(pyqt5_path, 'Qt5', 'plugins')
    if os.path.exists(plugins_path):
        os.environ['QT_PLUGIN_PATH'] = plugins_path
except:
    pass

write_log("Попытка импорта PyQt5...")
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
        QCheckBox, QComboBox, QSplitter, QMenuBar, QStatusBar, QMessageBox,
        QHeaderView, QGroupBox, QAction, QFileDialog, QDialog, QTextBrowser
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QIcon
    PYQT_VERSION = 5
    write_log("PyQt5 успешно импортирован")
except ImportError as e:
    log_error(f"Ошибка импорта PyQt5: {e}", exc_info=True)
    raise

import db
import models
import network
import export
import markdown
from version import __version__
from windows import ManagePromptsWindow, ManageModelsWindow, ViewResultsWindow, PromptImproverDialog, SettingsWindow


class RequestThread(QThread):
    """Поток для асинхронной отправки запросов к API."""
    finished = pyqtSignal(list)  # Сигнал с результатами запросов
    
    def __init__(self, models_list, prompt):
        super().__init__()
        self.models_list = models_list
        self.prompt = prompt
    
    def run(self):
        """Выполняет запросы к API в отдельном потоке."""
        results = network.send_prompt_to_multiple_models(
            self.models_list, 
            self.prompt,
            timeout=30
        )
        self.finished.emit(results)


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self):
        super().__init__()
        self.temp_results = []  # Временная таблица результатов в памяти
        self.current_prompt_id = None  # ID текущего промта (если выбран из сохраненных)
        
        self.init_ui()
        self.init_database()
        self.load_settings()  # Загружаем настройки перед загрузкой остальных элементов
        self.load_saved_prompts()
        self.load_models()
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        self.setWindowTitle("ChatList - Сравнение ответов нейросетей")
        self.setGeometry(100, 100, 1200, 800)
        
        # Устанавливаем иконку приложения
        icon_path = os.path.join(application_path, "app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Если иконка не найдена, пытаемся найти в текущей директории
            if os.path.exists("app.ico"):
                self.setWindowIcon(QIcon("app.ico"))
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Создаем разделитель для областей
        if PYQT_VERSION == 5:
            splitter = QSplitter(Qt.Orientation.Vertical)
        else:
            splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # ========== Область ввода промта ==========
        prompt_group = QGroupBox("Ввод промта")
        prompt_layout = QVBoxLayout()
        prompt_group.setLayout(prompt_layout)
        
        # Выбор сохраненного промта
        saved_prompt_layout = QHBoxLayout()
        saved_prompt_layout.addWidget(QLabel("Выбрать сохраненный промт:"))
        self.saved_prompts_combo = QComboBox()
        self.saved_prompts_combo.addItem("-- Новый промт --", None)
        self.saved_prompts_combo.currentIndexChanged.connect(self.on_prompt_selected)
        saved_prompt_layout.addWidget(self.saved_prompts_combo)
        prompt_layout.addLayout(saved_prompt_layout)
        
        # Текстовое поле для ввода промта
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Введите ваш промт здесь...")
        self.prompt_input.setMaximumHeight(150)
        prompt_layout.addWidget(self.prompt_input)
        
        # Поле для тегов
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Теги (через запятую):"))
        self.tags_input = QTextEdit()
        self.tags_input.setPlaceholderText("например: наука, физика, обучение")
        self.tags_input.setMaximumHeight(40)
        tags_layout.addWidget(self.tags_input)
        prompt_layout.addLayout(tags_layout)
        
        # Кнопки для работы с промтом
        prompt_buttons_layout = QHBoxLayout()
        
        self.improve_prompt_btn = QPushButton("Улучшить промт")
        self.improve_prompt_btn.clicked.connect(self.show_improve_prompt_dialog)
        self.improve_prompt_btn.setToolTip("Улучшить промт с помощью AI-ассистента")
        prompt_buttons_layout.addWidget(self.improve_prompt_btn)
        
        self.save_prompt_btn = QPushButton("Сохранить промт")
        self.save_prompt_btn.clicked.connect(self.save_prompt)
        prompt_buttons_layout.addWidget(self.save_prompt_btn)
        prompt_buttons_layout.addStretch()
        prompt_layout.addLayout(prompt_buttons_layout)
        
        splitter.addWidget(prompt_group)
        
        # ========== Область выбора моделей ==========
        models_group = QGroupBox("Выбор моделей")
        models_layout = QVBoxLayout()
        models_group.setLayout(models_layout)
        
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(3)
        self.models_table.setHorizontalHeaderLabels(["Выбрать", "Название", "Тип"])
        if PYQT_VERSION == 5:
            self.models_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        else:
            self.models_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.models_table.setMaximumHeight(150)
        models_layout.addWidget(self.models_table)
        
        splitter.addWidget(models_group)
        
        # ========== Область результатов ==========
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Модель", "Ответ", "Выбрано", "Действия"])
        if PYQT_VERSION == 5:
            self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        else:
            self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)
        
        splitter.addWidget(results_group)
        
        # Настройка пропорций разделителя
        splitter.setSizes([200, 150, 450])
        
        # ========== Кнопки управления ==========
        buttons_layout = QHBoxLayout()
        
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_requests)
        self.send_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        buttons_layout.addWidget(self.send_btn)
        
        self.save_results_btn = QPushButton("Сохранить выбранные")
        self.save_results_btn.clicked.connect(self.save_selected_results)
        self.save_results_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_results_btn)
        
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_results)
        buttons_layout.addWidget(self.clear_btn)
        
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        
        # ========== Меню ==========
        self.create_menu_bar()
        
        # ========== Статус-бар ==========
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")
    
    def create_menu_bar(self):
        """Создает меню приложения."""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        new_action = QAction("Новый промт", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_prompt)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Настройки"
        settings_menu = menubar.addMenu("Настройки")
        
        manage_models_action = QAction("Управление моделями", self)
        manage_models_action.triggered.connect(self.show_manage_models)
        settings_menu.addAction(manage_models_action)
        
        manage_prompts_action = QAction("Управление промтами", self)
        manage_prompts_action.triggered.connect(self.show_manage_prompts)
        settings_menu.addAction(manage_prompts_action)
        
        view_results_action = QAction("Просмотр сохраненных результатов", self)
        view_results_action.triggered.connect(self.show_saved_results)
        settings_menu.addAction(view_results_action)
        
        settings_menu.addSeparator()
        
        export_md_action = QAction("Экспорт результатов (Markdown)", self)
        export_md_action.triggered.connect(self.export_results_markdown)
        settings_menu.addAction(export_md_action)
        
        export_json_action = QAction("Экспорт результатов (JSON)", self)
        export_json_action.triggered.connect(self.export_results_json)
        settings_menu.addAction(export_json_action)
        
        settings_menu.addSeparator()
        
        app_settings_action = QAction("Настройки приложения", self)
        app_settings_action.triggered.connect(self.show_app_settings)
        settings_menu.addAction(app_settings_action)
        
        # Меню "Помощь"
        help_menu = menubar.addMenu("Помощь")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_database(self):
        """Инициализирует базу данных."""
        try:
            db.init_database()
            self.status_bar.showMessage("База данных инициализирована", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось инициализировать БД: {str(e)}")
    
    def load_saved_prompts(self):
        """Загружает сохраненные промты в выпадающий список."""
        try:
            prompts = db.get_all_prompts()
            self.saved_prompts_combo.clear()
            self.saved_prompts_combo.addItem("-- Новый промт --", None)
            
            for prompt in prompts:
                prompt_text = prompt['prompt'][:50] + "..." if len(prompt['prompt']) > 50 else prompt['prompt']
                display_text = f"{prompt['date']} - {prompt_text}"
                self.saved_prompts_combo.addItem(display_text, prompt['id'])
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки промтов: {str(e)}", 5000)
    
    def load_models(self):
        """Загружает модели в таблицу выбора."""
        try:
            all_models = models.ModelManager.get_all_models()
            self.models_table.setRowCount(len(all_models))
            
            for row, model in enumerate(all_models):
                # Чекбокс для выбора
                checkbox = QCheckBox()
                checkbox.setChecked(bool(model['is_active']))
                self.models_table.setCellWidget(row, 0, checkbox)
                
                # Название модели
                name_item = QTableWidgetItem(model['name'])
                if PYQT_VERSION == 5:
                    name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.models_table.setItem(row, 1, name_item)
                
                # Тип модели
                model_type = model.get('model_type', 'unknown')
                type_item = QTableWidgetItem(model_type)
                if PYQT_VERSION == 5:
                    type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
                self.models_table.setItem(row, 2, type_item)
            
            self.models_table.resizeColumnsToContents()
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки моделей: {str(e)}", 5000)
    
    def on_prompt_selected(self, index):
        """Обработчик выбора сохраненного промта."""
        prompt_id = self.saved_prompts_combo.itemData(index)
        if prompt_id:
            try:
                prompt = db.get_prompt(prompt_id)
                if prompt:
                    self.prompt_input.setPlainText(prompt['prompt'])
                    if prompt.get('tags'):
                        self.tags_input.setPlainText(prompt['tags'])
                    else:
                        self.tags_input.clear()
                    self.current_prompt_id = prompt_id
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить промт: {str(e)}")
        else:
            self.current_prompt_id = None
            self.tags_input.clear()
    
    def save_prompt(self):
        """Сохраняет текущий промт в БД."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Промт не может быть пустым")
            return
        
        tags_text = self.tags_input.toPlainText().strip()
        tags = tags_text if tags_text else None
        
        try:
            if self.current_prompt_id:
                # Обновляем существующий промт
                db.update_prompt(self.current_prompt_id, prompt_text=prompt_text, tags=tags)
                self.status_bar.showMessage("Промт обновлен", 3000)
            else:
                # Создаем новый промт
                prompt_id = db.create_prompt(prompt_text, tags)
                self.current_prompt_id = prompt_id
                self.status_bar.showMessage("Промт сохранен", 3000)
            
            self.load_saved_prompts()
            # Выбираем текущий промт
            if self.current_prompt_id:
                for i in range(self.saved_prompts_combo.count()):
                    if self.saved_prompts_combo.itemData(i) == self.current_prompt_id:
                        self.saved_prompts_combo.setCurrentIndex(i)
                        break
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить промт: {str(e)}")
    
    def get_selected_models(self):
        """Возвращает список выбранных моделей с их API-ключами."""
        selected_models = []
        all_models = models.ModelManager.get_all_models()
        
        # Проверяем наличие OPENROUTER_API_KEY один раз
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if not openrouter_key:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "OPENROUTER_API_KEY не найден в файле .env.\n\n"
                "Все модели используют OpenRouter, поэтому необходим ключ OPENROUTER_API_KEY.\n"
                "Добавьте его в файл .env для работы с моделями."
            )
            return []
        
        for row in range(self.models_table.rowCount()):
            checkbox = self.models_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                model = all_models[row]
                model_with_key = models.ModelManager.get_model_with_key(model['id'])
                if model_with_key:
                    # Принудительно используем OpenRouter для всех моделей
                    model_with_key['api_key'] = openrouter_key
                    model_with_key['api_url'] = 'https://openrouter.ai/api/v1/chat/completions'
                    model_with_key['model_type'] = 'openrouter'
                    
                    selected_models.append(model_with_key)
        
        return selected_models
    
    def send_requests(self):
        """Отправляет промт во все выбранные модели."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Введите промт перед отправкой")
            return
        
        selected_models = self.get_selected_models()
        if not selected_models:
            QMessageBox.warning(self, "Предупреждение", "Выберите хотя бы одну модель")
            return
        
        # Очищаем предыдущие результаты
        self.clear_results()
        
        # Сохраняем промт, если он новый
        if not self.current_prompt_id:
            try:
                self.current_prompt_id = db.create_prompt(prompt_text)
            except Exception as e:
                QMessageBox.warning(self, "Предупреждение", f"Не удалось сохранить промт: {str(e)}")
        
        # Блокируем кнопку отправки
        self.send_btn.setEnabled(False)
        self.status_bar.showMessage("Отправка запросов...")
        
        # Создаем поток для асинхронной отправки
        self.request_thread = RequestThread(selected_models, prompt_text)
        self.request_thread.finished.connect(self.on_requests_finished)
        self.request_thread.start()
    
    def on_requests_finished(self, results):
        """Обработчик завершения запросов."""
        self.send_btn.setEnabled(True)
        self.temp_results = results
        
        # Обновляем таблицу результатов
        self.results_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # Название модели
            model_item = QTableWidgetItem(result['model_name'])
            if PYQT_VERSION == 5:
                model_item.setFlags(model_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            else:
                model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 0, model_item)
            
            # Ответ - используем QTextEdit для многострочного отображения
            if result['success']:
                response_text = result['response']
            else:
                response_text = f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"
            
            # Создаем QTextEdit для отображения многострочного текста
            response_widget = QTextEdit()
            response_widget.setPlainText(response_text)
            response_widget.setReadOnly(True)
            
            # Убираем рамку вокруг текста для более чистого вида в таблице
            if PYQT_VERSION == 5:
                response_widget.setFrameShape(QTextEdit.Shape.NoFrame)
                response_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                response_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            else:
                response_widget.setFrameShape(QTextEdit.NoFrame)
                response_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                response_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # QTextEdit по умолчанию поддерживает перенос текста по словам
            # Явно включаем перенос, если нужно
            try:
                if PYQT_VERSION == 5:
                    from PyQt5.QtGui import QTextOption
                    response_widget.setWordWrapMode(QTextOption.WrapMode.WordWrap)
                else:
                    from PyQt5.QtGui import QTextOption
                    response_widget.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            except:
                pass  # Используем настройки по умолчанию
            
            # Устанавливаем стиль для более чистого вида
            response_widget.setStyleSheet("background-color: transparent; border: none; padding: 2px;")
            
            # Рассчитываем высоту на основе количества строк текста
            lines = response_text.count('\n') + 1
            # Оцениваем количество строк с учетом переноса (примерно 80 символов на строку)
            text_length = len(response_text)
            estimated_lines = max(lines, (text_length // 80) + 1) if text_length > 0 else 1
            
            min_height = 60  # Минимальная высота
            max_height = 500  # Максимальная высота
            # Оцениваем высоту: примерно 22-24 пикселя на строку
            estimated_height = min(max(min_height, estimated_lines * 23), max_height)
            
            response_widget.setMinimumHeight(min_height)
            response_widget.setMaximumHeight(max_height)
            
            self.results_table.setCellWidget(row, 1, response_widget)
            self.results_table.setRowHeight(row, estimated_height)
            
            # Чекбокс для выбора
            checkbox = QCheckBox()
            checkbox.setChecked(result['success'])  # Автоматически выбираем успешные ответы
            self.results_table.setCellWidget(row, 2, checkbox)
            
            # Кнопка "Открыть" для просмотра ответа в markdown
            open_btn = QPushButton("Открыть")
            open_btn.clicked.connect(lambda checked, r=result, rt=response_text: self.open_response_markdown(r, rt))
            self.results_table.setCellWidget(row, 3, open_btn)
        
        self.results_table.resizeColumnsToContents()
        self.save_results_btn.setEnabled(True)
        self.status_bar.showMessage(f"Получено ответов: {sum(1 for r in results if r['success'])}/{len(results)}", 5000)
    
    def save_selected_results(self):
        """Сохраняет выбранные результаты в БД."""
        if not self.current_prompt_id:
            QMessageBox.warning(self, "Предупреждение", "Нет активного промта для сохранения")
            return
        
        selected_count = 0
        errors = []
        
        for row in range(self.results_table.rowCount()):
            checkbox = self.results_table.cellWidget(row, 2)
            if checkbox and checkbox.isChecked():
                result = self.temp_results[row]
                if result['success']:
                    try:
                        db.create_result(
                            prompt_id=self.current_prompt_id,
                            model_id=result['model_id'],
                            response=result['response'],
                            tokens_used=result.get('tokens_used'),
                            response_time=result.get('response_time')
                        )
                        selected_count += 1
                    except Exception as e:
                        errors.append(f"{result['model_name']}: {str(e)}")
        
        if selected_count > 0:
            self.status_bar.showMessage(f"Сохранено результатов: {selected_count}", 5000)
            if errors:
                QMessageBox.warning(self, "Предупреждение", 
                                  f"Сохранено {selected_count} результатов.\nОшибки:\n" + "\n".join(errors))
            else:
                QMessageBox.information(self, "Успех", f"Сохранено результатов: {selected_count}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Не выбрано ни одного результата для сохранения")
    
    def clear_results(self):
        """Очищает таблицу результатов."""
        self.results_table.setRowCount(0)
        self.temp_results = []
        self.save_results_btn.setEnabled(False)
        self.status_bar.showMessage("Результаты очищены", 3000)
    
    def new_prompt(self):
        """Создает новый промт."""
        self.prompt_input.clear()
        self.tags_input.clear()
        self.saved_prompts_combo.setCurrentIndex(0)
        self.current_prompt_id = None
        self.clear_results()
    
    def show_manage_models(self):
        """Показывает окно управления моделями."""
        window = ManageModelsWindow(self)
        window.exec()
        self.load_models()  # Обновляем список моделей после закрытия окна
    
    def show_manage_prompts(self):
        """Показывает окно управления промтами."""
        window = ManagePromptsWindow(self)
        window.exec()
        self.load_saved_prompts()  # Обновляем список промтов после закрытия окна
    
    def show_saved_results(self):
        """Показывает окно просмотра сохраненных результатов."""
        window = ViewResultsWindow(self)
        window.exec()
    
    def load_settings(self):
        """Загружает настройки из БД и применяет их."""
        try:
            # Загружаем тему
            theme = db.get_setting("theme") or "light"  # По умолчанию светлая
            self.apply_theme(theme)
            
            # Загружаем размер шрифта
            font_size = db.get_setting("font_size") or "10"  # По умолчанию 10 pt
            self.apply_font_size(int(font_size))
        except Exception as e:
            # Если не удалось загрузить настройки, используем значения по умолчанию
            self.status_bar.showMessage(f"Не удалось загрузить настройки: {str(e)}", 5000)
    
    def apply_theme(self, theme: str):
        """
        Применяет тему к приложению.
        
        Args:
            theme: 'light' или 'dark'
        """
        if theme == "dark":
            # Тёмная тема
            dark_stylesheet = """
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QTextEdit, QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QTableWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                gridline-color: #555555;
            }
            QTableWidget::item {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTableWidget::item:selected {
                background-color: #555555;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #555555;
            }
            QCheckBox {
                color: #ffffff;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 5px 10px;
            }
            QTabBar::tab:selected {
                background-color: #555555;
            }
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            """
            self.setStyleSheet(dark_stylesheet)
        else:
            # Светлая тема (по умолчанию, стили Qt)
            self.setStyleSheet("")
    
    def apply_font_size(self, font_size: int):
        """
        Применяет размер шрифта к панелям приложения.
        
        Args:
            font_size: Размер шрифта в пунктах
        """
        try:
            if PYQT_VERSION == 5:
                from PyQt5.QtGui import QFont
            else:
                from PyQt5.QtGui import QFont
            
            font = QFont()
            font.setPointSize(font_size)
            
            # Применяем шрифт ко всем виджетам
            self.setFont(font)
            
            # Также применяем к основным элементам интерфейса
            self.prompt_input.setFont(font)
            self.tags_input.setFont(font)
            
            # Применяем к таблицам (но немного меньше, так как там много текста)
            table_font = QFont()
            table_font.setPointSize(max(font_size - 1, 8))  # Минимум 8pt
            
            self.models_table.setFont(table_font)
            self.results_table.setFont(table_font)
            
        except Exception as e:
            self.status_bar.showMessage(f"Не удалось применить размер шрифта: {str(e)}", 5000)
    
    def show_app_settings(self):
        """Показывает окно настроек приложения."""
        window = SettingsWindow(self)
        
        # Проверяем результат диалога (совместимость с PyQt5 и PyQt6)
        if PYQT_VERSION == 5:
            result = window.exec() == QDialog.DialogCode.Accepted
        else:
            result = window.exec() == QDialog.Accepted
        
        # Настройки уже применены в окне настроек, просто перезагружаем для полноты
        # (хотя они уже должны быть применены)
        if result:
            # Перезагружаем настройки на случай, если они были изменены
            self.load_settings()
    
    def export_results_markdown(self):
        """Экспортирует сохраненные результаты в Markdown."""
        try:
            results = db.get_all_results()
            if not results:
                QMessageBox.information(self, "Информация", "Нет сохраненных результатов для экспорта")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как Markdown", "results.md", "Markdown Files (*.md);;All Files (*)"
            )
            
            if filename:
                export.export_results_to_markdown(results, filename)
                QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать результаты: {str(e)}")
    
    def export_results_json(self):
        """Экспортирует сохраненные результаты в JSON."""
        try:
            results = db.get_all_results()
            if not results:
                QMessageBox.information(self, "Информация", "Нет сохраненных результатов для экспорта")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как JSON", "results.json", "JSON Files (*.json);;All Files (*)"
            )
            
            if filename:
                export.export_results_to_json(results, filename)
                QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать результаты: {str(e)}")
    
    def open_response_markdown(self, result, response_text):
        """Открывает ответ нейросети в окне с форматированным markdown."""
        dialog = MarkdownViewDialog(self, result, response_text)
        dialog.exec()
    
    def show_improve_prompt_dialog(self):
        """Показывает диалог улучшения промта."""
        prompt_text = self.prompt_input.toPlainText().strip()
        
        if not prompt_text:
            reply = QMessageBox.question(
                self,
                "Пустое поле",
                "Поле ввода промта пустое. Вы хотите ввести промт сейчас или открыть диалог улучшения?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.No:
                # Открываем диалог с пустым промтом (пользователь может ввести его там)
                prompt_text = ""
        
        # Проверяем наличие активных моделей
        try:
            active_models = models.ModelManager.get_active_models()
            if not active_models:
                QMessageBox.warning(
                    self,
                    "Предупреждение",
                    "Нет активных моделей. Добавьте хотя бы одну модель в настройках "
                    "перед использованием функции улучшения промтов."
                )
                return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось проверить активные модели: {str(e)}")
            return
        
        # Открываем диалог улучшения промта
        dialog = PromptImproverDialog(self, prompt_text)
        
        # Проверяем результат диалога (совместимость с PyQt5 и PyQt6)
        if PYQT_VERSION == 5:
            result = dialog.exec() == QDialog.DialogCode.Accepted
        else:
            result = dialog.exec() == QDialog.Accepted
        
        if result:
            # Если пользователь выбрал вариант для подстановки
            selected_prompt = dialog.get_selected_prompt()
            if selected_prompt:
                self.prompt_input.setPlainText(selected_prompt)
                self.status_bar.showMessage("Улучшенный промт подставлен в поле ввода", 3000)
    
    def show_about(self):
        """Показывает информацию о программе."""
        about_text = f"""
        <h2>ChatList</h2>
        <p><b>Версия:</b> {__version__}</p>
        <p><b>Описание:</b></p>
        <p>ChatList — это приложение для сравнения ответов нейросетей.</p>
        <p>Позволяет отправлять один промт в несколько нейросетей одновременно и сравнивать их ответы в удобной таблице.</p>
        
        <p><b>Основные возможности:</b></p>
        <ul>
            <li>Отправка промта в несколько моделей одновременно</li>
            <li>Сравнение ответов в табличном виде</li>
            <li>Сохранение выбранных результатов в базу данных</li>
            <li>Управление промтами и моделями</li>
            <li>AI-ассистент для улучшения промтов</li>
            <li>Экспорт результатов в Markdown и JSON</li>
            <li>Настройка темы и размера шрифта</li>
        </ul>
        
        <p><b>Технологии:</b></p>
        <ul>
            <li>Python 3.11+</li>
            <li>PyQt5</li>
            <li>SQLite</li>
            <li>OpenRouter API</li>
        </ul>
        
        <p><b>Автор:</b> ChatList Team</p>
        <p><b>Лицензия:</b> См. файл LICENSE</p>
        """
        
        QMessageBox.about(self, "О программе ChatList", about_text)


class MarkdownViewDialog(QDialog):
    """Диалог для просмотра ответа в форматированном markdown."""
    
    def __init__(self, parent=None, result=None, response_text=""):
        super().__init__(parent)
        self.result = result
        self.response_text = response_text
        self.setWindowTitle(f"Ответ: {result.get('model_name', 'Неизвестная модель')}" if result else "Ответ нейросети")
        self.setGeometry(100, 100, 900, 700)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок с информацией о модели
        if self.result:
            info_label = QLabel(f"<b>Модель:</b> {self.result.get('model_name', 'Неизвестная модель')}")
            layout.addWidget(info_label)
        
        # QTextBrowser для отображения HTML (конвертированного из markdown)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Кнопка копирования
        copy_btn = QPushButton("Копировать текст")
        copy_btn.clicked.connect(self.copy_text)
        buttons_layout.addWidget(copy_btn)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Конвертируем markdown в HTML и отображаем
        self.render_markdown()
    
    def render_markdown(self):
        """Конвертирует markdown в HTML и отображает в браузере."""
        try:
            # Конвертируем markdown в HTML
            html_content = markdown.markdown(
                self.response_text,
                extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
            )
            
            # Добавляем стили для лучшего отображения
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        font-size: 14px;
                        line-height: 1.6;
                        color: #333;
                        padding: 20px;
                        max-width: 100%;
                        margin: 0 auto;
                    }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                        font-size: 13px;
                    }}
                    pre {{
                        background-color: #f4f4f4;
                        padding: 12px;
                        border-radius: 5px;
                        overflow-x: auto;
                        border-left: 4px solid #2196F3;
                    }}
                    pre code {{
                        background-color: transparent;
                        padding: 0;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        margin-top: 24px;
                        margin-bottom: 16px;
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 10px; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }}
                    h3 {{ font-size: 1.25em; }}
                    p {{ margin-bottom: 16px; }}
                    ul, ol {{
                        margin-bottom: 16px;
                        padding-left: 30px;
                    }}
                    li {{ margin-bottom: 4px; }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin-bottom: 16px;
                    }}
                    th, td {{
                        border: 1px solid #dfe2e5;
                        padding: 8px 12px;
                    }}
                    th {{
                        background-color: #f6f8fa;
                        font-weight: 600;
                    }}
                    blockquote {{
                        margin: 0;
                        padding: 0 16px;
                        color: #6a737d;
                        border-left: 4px solid #dfe2e5;
                    }}
                    a {{
                        color: #0366d6;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    hr {{
                        border: none;
                        border-top: 1px solid #eaecef;
                        margin: 24px 0;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            self.browser.setHtml(styled_html)
        except Exception as e:
            # Если произошла ошибка при конвертации, показываем обычный текст
            error_message = f"Ошибка при форматировании markdown: {str(e)}\n\nИсходный текст:\n\n{self.response_text}"
            self.browser.setPlainText(error_message)
    
    def copy_text(self):
        """Копирует исходный текст в буфер обмена."""
        app = QApplication.instance()
        if app:
            clipboard = app.clipboard()
            clipboard.setText(self.response_text)
            QMessageBox.information(self, "Успех", "Текст скопирован в буфер обмена")


def main():
    """Главная функция приложения."""
    import logging
    import traceback

    # Настраиваем логирование с выводом в файл и консоль
    # Используем глобальный log_file, который уже настроен правильно (пользовательская директория)
    # Если log_file не определен, используем пользовательскую директорию
    if log_file is None or not log_file:
        user_data_dir = os.path.join(os.environ.get('APPDATA', ''), 'ChatList')
        try:
            os.makedirs(user_data_dir, exist_ok=True)
            main_log_file = os.path.join(user_data_dir, 'chatlist.log')
        except:
            import tempfile
            main_log_file = os.path.join(tempfile.gettempdir(), 'chatlist.log')
    else:
        main_log_file = log_file
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(main_log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stderr)
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Запуск ChatList версии {__version__}")
        logger.info(f"Путь к приложению: {application_path}")
        logger.info(f"Python версия: {sys.version}")
        
        app = QApplication(sys.argv)
        
        # Устанавливаем иконку приложения для всех окон
        icon_path = os.path.join(application_path, "app.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        elif os.path.exists("app.ico"):
            app.setWindowIcon(QIcon("app.ico"))
        
        # Убеждаемся, что приложение видимо
        if not app.instance():
            app.setQuitOnLastWindowClosed(True)
        
        window = MainWindow()
        window.show()
        window.raise_()  # Поднимаем окно на передний план
        window.activateWindow()  # Активируем окно
        
        logger.info("Окно приложения создано и отображено")
        sys.exit(app.exec())
    except Exception as e:
        error_msg = f"Критическая ошибка при запуске: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        
        # Показываем сообщение об ошибке, если возможно
        try:
            if 'app' in locals():
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(None, "Ошибка запуска", error_msg)
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Обработка исключений на самом верхнем уровне
        try:
            log_error(f"Необработанное исключение в main(): {e}", exc_info=True)
        except:
            # Если даже логирование не работает, выводим в stderr
            traceback.print_exc(file=sys.stderr)
        
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(f"\nЛог файл: {log_file}", file=sys.stderr)
        print("\nНажмите Enter для закрытия окна...", file=sys.stderr)
        try:
            input()
        except:
            try:
                time.sleep(30)
            except:
                pass
        sys.exit(1)
