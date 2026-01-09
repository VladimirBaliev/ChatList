"""
Главный модуль приложения ChatList.
Содержит основной интерфейс пользователя.
"""
import sys
import os

# Устанавливаем рабочую директорию на директорию скрипта
if getattr(sys, 'frozen', False):
    # Если программа запущена как exe
    application_path = os.path.dirname(sys.executable)
else:
    # Если программа запущена как скрипт
    application_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(application_path)

# Настраиваем путь к плагинам Qt для PyQt5
try:
    import PyQt5
    pyqt5_path = os.path.dirname(PyQt5.__file__)
    plugins_path = os.path.join(pyqt5_path, 'Qt5', 'plugins')
    if os.path.exists(plugins_path):
        os.environ['QT_PLUGIN_PATH'] = plugins_path
except:
    pass

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
        QCheckBox, QComboBox, QSplitter, QMenuBar, QStatusBar, QMessageBox,
        QHeaderView, QGroupBox
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QAction
    PYQT_VERSION = 6
except ImportError:
    # Fallback на PyQt5 если PyQt6 не доступен
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
        QCheckBox, QComboBox, QSplitter, QMenuBar, QStatusBar, QMessageBox,
        QHeaderView, QGroupBox, QAction, QFileDialog
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    PYQT_VERSION = 5

import db
import models
import network
import export
from windows import ManagePromptsWindow, ManageModelsWindow, ViewResultsWindow


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
        self.load_saved_prompts()
        self.load_models()
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        self.setWindowTitle("ChatList - Сравнение ответов нейросетей")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Создаем разделитель для областей
        if PYQT_VERSION == 6:
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
        if PYQT_VERSION == 6:
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
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Модель", "Ответ", "Выбрано"])
        if PYQT_VERSION == 6:
            self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        else:
            self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
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
                if PYQT_VERSION == 6:
                    name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.models_table.setItem(row, 1, name_item)
                
                # Тип модели
                model_type = model.get('model_type', 'unknown')
                type_item = QTableWidgetItem(model_type)
                if PYQT_VERSION == 6:
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
            if PYQT_VERSION == 6:
                model_item.setFlags(model_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            else:
                model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 0, model_item)
            
            # Ответ
            if result['success']:
                response_text = result['response']
            else:
                response_text = f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"
            
            response_item = QTableWidgetItem(response_text)
            if PYQT_VERSION == 6:
                response_item.setFlags(response_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            else:
                response_item.setFlags(response_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 1, response_item)
            
            # Чекбокс для выбора
            checkbox = QCheckBox()
            checkbox.setChecked(result['success'])  # Автоматически выбираем успешные ответы
            self.results_table.setCellWidget(row, 2, checkbox)
        
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
    
    def show_app_settings(self):
        """Показывает окно настроек приложения (заглушка)."""
        QMessageBox.information(self, "Настройки", 
                              "Функция будет реализована в следующих этапах")
    
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
    
    def show_about(self):
        """Показывает информацию о программе."""
        QMessageBox.about(self, "О программе ChatList",
                        "ChatList - приложение для сравнения ответов нейросетей\n\n"
                        "Версия: 1.0.0\n"
                        "Позволяет отправлять один промт в несколько нейросетей\n"
                        "и сравнивать их ответы.")


def main():
    """Главная функция приложения."""
    app = QApplication(sys.argv)
    
    # Убеждаемся, что приложение видимо
    if not app.instance():
        app.setQuitOnLastWindowClosed(True)
    
    window = MainWindow()
    window.show()
    window.raise_()  # Поднимаем окно на передний план
    window.activateWindow()  # Активируем окно
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
