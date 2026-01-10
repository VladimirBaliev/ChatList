"""
Модуль с окнами управления для ChatList.
Содержит окна для управления промтами, моделями, результатами и настройками.
"""
import sys
from typing import Optional
import db
import models
import prompt_improver

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
        QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox,
        QMessageBox, QHeaderView, QGroupBox, QProgressBar, QTabWidget, QWidget
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
        QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox,
        QMessageBox, QHeaderView, QGroupBox, QProgressBar, QTabWidget, QWidget
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    PYQT_VERSION = 5


class ManagePromptsWindow(QDialog):
    """Окно для управления промтами."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление промтами")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.load_prompts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Поиск и фильтры
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.filter_prompts)
        search_layout.addWidget(self.search_input)
        
        search_layout.addWidget(QLabel("Теги:"))
        self.tags_filter = QLineEdit()
        self.tags_filter.setPlaceholderText("Фильтр по тегам...")
        self.tags_filter.textChanged.connect(self.filter_prompts)
        search_layout.addWidget(self.tags_filter)
        
        layout.addLayout(search_layout)
        
        # Таблица промтов
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Дата", "Промт", "Теги", "Действия"])
        if PYQT_VERSION == 6:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        else:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Удалить выбранные")
        self.delete_btn.clicked.connect(self.delete_selected)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)
        layout.addLayout(buttons_layout)
    
    def load_prompts(self):
        """Загружает промты в таблицу."""
        try:
            prompts = db.get_all_prompts()
            self.table.setRowCount(len(prompts))
            
            for row, prompt in enumerate(prompts):
                # Дата
                date_item = QTableWidgetItem(prompt['date'])
                if PYQT_VERSION == 6:
                    date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 0, date_item)
                
                # Промт
                prompt_text = prompt['prompt'][:100] + "..." if len(prompt['prompt']) > 100 else prompt['prompt']
                prompt_item = QTableWidgetItem(prompt_text)
                prompt_item.setData(Qt.ItemDataRole.UserRole, prompt['id'])
                if PYQT_VERSION == 6:
                    prompt_item.setFlags(prompt_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    prompt_item.setFlags(prompt_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 1, prompt_item)
                
                # Теги
                tags_item = QTableWidgetItem(prompt.get('tags', '') or '')
                if PYQT_VERSION == 6:
                    tags_item.setFlags(tags_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    tags_item.setFlags(tags_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 2, tags_item)
                
                # Кнопка редактирования
                edit_btn = QPushButton("Редактировать")
                edit_btn.clicked.connect(lambda checked, p=prompt: self.edit_prompt(p))
                self.table.setCellWidget(row, 3, edit_btn)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить промты: {str(e)}")
    
    def filter_prompts(self):
        """Фильтрует промты по поисковому запросу и тегам."""
        search_text = self.search_input.text().lower()
        tags_text = self.tags_filter.text().lower()
        
        for row in range(self.table.rowCount()):
            prompt_item = self.table.item(row, 1)
            tags_item = self.table.item(row, 2)
            
            if prompt_item and tags_item:
                prompt_text = prompt_item.text().lower()
                tags = tags_item.text().lower()
                
                show = True
                if search_text and search_text not in prompt_text:
                    show = False
                if tags_text and tags_text not in tags:
                    show = False
                
                self.table.setRowHidden(row, not show)
    
    def edit_prompt(self, prompt):
        """Редактирует промт."""
        dialog = EditPromptDialog(self, prompt)
        if PYQT_VERSION == 6:
            result = dialog.exec() == QDialog.DialogCode.Accepted
        else:
            result = dialog.exec() == QDialog.Accepted
        if result:
            self.load_prompts()
    
    def delete_selected(self):
        """Удаляет выбранные промты."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите промты для удаления")
            return
        
        reply = QMessageBox.question(self, "Подтверждение", 
                                   f"Удалить {len(selected_rows)} промт(ов)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            for row in selected_rows:
                prompt_item = self.table.item(row, 1)
                if prompt_item:
                    prompt_id = prompt_item.data(Qt.ItemDataRole.UserRole)
                    try:
                        db.delete_prompt(prompt_id)
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Не удалось удалить промт: {str(e)}")
            self.load_prompts()


class EditPromptDialog(QDialog):
    """Диалог редактирования промта."""
    
    def __init__(self, parent=None, prompt=None):
        super().__init__(parent)
        self.prompt = prompt
        self.setWindowTitle("Редактировать промт" if prompt else "Новый промт")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel("Промт:"))
        self.prompt_input = QTextEdit()
        if self.prompt:
            self.prompt_input.setPlainText(self.prompt['prompt'])
        layout.addWidget(self.prompt_input)
        
        layout.addWidget(QLabel("Теги:"))
        self.tags_input = QLineEdit()
        if self.prompt and self.prompt.get('tags'):
            self.tags_input.setText(self.prompt['tags'])
        layout.addWidget(self.tags_input)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def save(self):
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Промт не может быть пустым")
            return
        
        tags = self.tags_input.text().strip() or None
        
        try:
            if self.prompt:
                db.update_prompt(self.prompt['id'], prompt_text=prompt_text, tags=tags)
            else:
                db.create_prompt(prompt_text, tags)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить промт: {str(e)}")


class ManageModelsWindow(QDialog):
    """Окно для управления моделями."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление моделями")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()
        self.load_models()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Таблица моделей
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Активна", "Название", "API URL", "API ID", "Тип", "Действия"])
        if PYQT_VERSION == 6:
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        else:
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить модель")
        add_btn.clicked.connect(self.add_model)
        buttons_layout.addWidget(add_btn)
        
        self.delete_btn = QPushButton("Удалить выбранные")
        self.delete_btn.clicked.connect(self.delete_selected)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
    
    def load_models(self):
        """Загружает модели в таблицу."""
        try:
            all_models = models.ModelManager.get_all_models()
            self.table.setRowCount(len(all_models))
            
            for row, model in enumerate(all_models):
                # Чекбокс активности
                checkbox = QCheckBox()
                checkbox.setChecked(bool(model['is_active']))
                checkbox.stateChanged.connect(lambda state, m=model: self.toggle_active(m['id'], state))
                self.table.setCellWidget(row, 0, checkbox)
                
                # Название
                name_item = QTableWidgetItem(model['name'])
                name_item.setData(Qt.ItemDataRole.UserRole, model['id'])
                if PYQT_VERSION == 6:
                    name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 1, name_item)
                
                # API URL
                url_item = QTableWidgetItem(model['api_url'])
                if PYQT_VERSION == 6:
                    url_item.setFlags(url_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    url_item.setFlags(url_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 2, url_item)
                
                # API ID
                api_id_item = QTableWidgetItem(model['api_id'])
                if PYQT_VERSION == 6:
                    api_id_item.setFlags(api_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    api_id_item.setFlags(api_id_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 3, api_id_item)
                
                # Тип
                type_item = QTableWidgetItem(model.get('model_type', 'unknown'))
                if PYQT_VERSION == 6:
                    type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 4, type_item)
                
                # Кнопка редактирования
                edit_btn = QPushButton("Редактировать")
                edit_btn.clicked.connect(lambda checked, m=model: self.edit_model(m))
                self.table.setCellWidget(row, 5, edit_btn)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модели: {str(e)}")
    
    def toggle_active(self, model_id, state):
        """Переключает активность модели."""
        try:
            models.ModelManager.update_model(model_id, is_active=1 if state else 0)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить модель: {str(e)}")
    
    def add_model(self):
        """Добавляет новую модель."""
        dialog = EditModelDialog(self)
        if PYQT_VERSION == 6:
            result = dialog.exec() == QDialog.DialogCode.Accepted
        else:
            result = dialog.exec() == QDialog.Accepted
        if result:
            self.load_models()
    
    def edit_model(self, model):
        """Редактирует модель."""
        dialog = EditModelDialog(self, model)
        if PYQT_VERSION == 6:
            result = dialog.exec() == QDialog.DialogCode.Accepted
        else:
            result = dialog.exec() == QDialog.Accepted
        if result:
            self.load_models()
    
    def delete_selected(self):
        """Удаляет выбранные модели."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите модели для удаления")
            return
        
        reply = QMessageBox.question(self, "Подтверждение",
                                   f"Удалить {len(selected_rows)} модель(ей)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            for row in selected_rows:
                name_item = self.table.item(row, 1)
                if name_item:
                    model_id = name_item.data(Qt.ItemDataRole.UserRole)
                    try:
                        models.ModelManager.delete_model(model_id)
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Не удалось удалить модель: {str(e)}")
            self.load_models()


class EditModelDialog(QDialog):
    """Диалог редактирования модели."""
    
    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Редактировать модель" if model else "Добавить модель")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        if self.model:
            self.name_input.setText(self.model['name'])
        else:
            self.name_input.setPlaceholderText("Например: mistralai/devstral-2512 или qwen/qwen3-coder")
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("API URL:"))
        self.url_input = QLineEdit()
        if self.model:
            self.url_input.setText(self.model['api_url'])
        else:
            self.url_input.setPlaceholderText("https://openrouter.ai/api/v1/chat/completions")
            self.url_input.setText("https://openrouter.ai/api/v1/chat/completions")
        layout.addWidget(self.url_input)
        
        layout.addWidget(QLabel("API ID (имя переменной окружения):"))
        self.api_id_input = QLineEdit()
        if self.model:
            self.api_id_input.setText(self.model['api_id'])
        else:
            self.api_id_input.setPlaceholderText("OPENROUTER_API_KEY")
            self.api_id_input.setText("OPENROUTER_API_KEY")
        layout.addWidget(self.api_id_input)
        
        layout.addWidget(QLabel("Тип модели:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['openrouter', 'openai', 'deepseek', 'groq', 'unknown'])
        if self.model:
            model_type = self.model.get('model_type', 'unknown')
            index = self.type_combo.findText(model_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        else:
            self.type_combo.setCurrentIndex(0)  # По умолчанию openrouter
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)
        
        # Подсказка для названия модели
        hint_label = QLabel("Подсказка: Для OpenRouter используйте формат 'provider/model', например: 'mistralai/devstral-2512' или 'qwen/qwen3-coder'")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(hint_label)
        
        self.active_checkbox = QCheckBox("Активна")
        if self.model:
            self.active_checkbox.setChecked(bool(self.model.get('is_active', 1)))
        else:
            self.active_checkbox.setChecked(True)
        layout.addWidget(self.active_checkbox)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def on_type_changed(self, model_type):
        """Обновляет значения по умолчанию при изменении типа модели."""
        if not self.model:  # Только для новых моделей
            if model_type == 'openrouter':
                self.url_input.setText("https://openrouter.ai/api/v1/chat/completions")
                self.api_id_input.setText("OPENROUTER_API_KEY")
            elif model_type == 'openai':
                self.url_input.setText("https://api.openai.com/v1/chat/completions")
                self.api_id_input.setText("OPENAI_API_KEY")
            elif model_type == 'deepseek':
                self.url_input.setText("https://api.deepseek.com/v1/chat/completions")
                self.api_id_input.setText("DEEPSEEK_API_KEY")
            elif model_type == 'groq':
                self.url_input.setText("https://api.groq.com/openai/v1/chat/completions")
                self.api_id_input.setText("GROQ_API_KEY")
    
    def save(self):
        name = self.name_input.text().strip()
        api_url = self.url_input.text().strip()
        api_id = self.api_id_input.text().strip()
        model_type = self.type_combo.currentText()
        is_active = 1 if self.active_checkbox.isChecked() else 0
        
        if not name or not api_url or not api_id:
            QMessageBox.warning(self, "Предупреждение", "Заполните все обязательные поля")
            return
        
        try:
            if self.model:
                models.ModelManager.update_model(
                    self.model['id'],
                    name=name,
                    api_url=api_url,
                    api_id=api_id,
                    model_type=model_type,
                    is_active=is_active
                )
            else:
                models.ModelManager.create_model(
                    name, api_url, api_id, model_type, is_active
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить модель: {str(e)}")


class ViewResultsWindow(QDialog):
    """Окно для просмотра сохраненных результатов."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сохраненные результаты")
        self.setGeometry(100, 100, 1000, 700)
        self.init_ui()
        self.load_results()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Фильтры
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по тексту...")
        self.search_input.textChanged.connect(self.filter_results)
        filters_layout.addWidget(self.search_input)
        layout.addLayout(filters_layout)
        
        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Дата", "Промт", "Модель", "Ответ", "Действия"])
        if PYQT_VERSION == 6:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        else:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        delete_btn = QPushButton("Удалить выбранные")
        delete_btn.clicked.connect(self.delete_selected)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
    
    def load_results(self):
        """Загружает результаты в таблицу."""
        try:
            results = db.get_all_results()
            self.table.setRowCount(len(results))
            
            for row, result in enumerate(results):
                # Дата
                date_item = QTableWidgetItem(result['saved_at'])
                if PYQT_VERSION == 6:
                    date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 0, date_item)
                
                # Промт
                prompt_text = result.get('prompt_text', '')[:50] + "..." if len(result.get('prompt_text', '')) > 50 else result.get('prompt_text', '')
                prompt_item = QTableWidgetItem(prompt_text)
                prompt_item.setData(Qt.ItemDataRole.UserRole, result['id'])
                if PYQT_VERSION == 6:
                    prompt_item.setFlags(prompt_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    prompt_item.setFlags(prompt_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 1, prompt_item)
                
                # Модель
                model_item = QTableWidgetItem(result.get('model_name', ''))
                if PYQT_VERSION == 6:
                    model_item.setFlags(model_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 2, model_item)
                
                # Ответ
                response_text = result['response'][:100] + "..." if len(result['response']) > 100 else result['response']
                response_item = QTableWidgetItem(response_text)
                if PYQT_VERSION == 6:
                    response_item.setFlags(response_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    response_item.setFlags(response_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 3, response_item)
                
                # Кнопка просмотра
                view_btn = QPushButton("Просмотр")
                view_btn.clicked.connect(lambda checked, r=result: self.view_result(r))
                self.table.setCellWidget(row, 4, view_btn)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить результаты: {str(e)}")
    
    def filter_results(self):
        """Фильтрует результаты по поисковому запросу."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            prompt_item = self.table.item(row, 1)
            response_item = self.table.item(row, 3)
            
            if prompt_item and response_item:
                prompt_text = prompt_item.text().lower()
                response_text = response_item.text().lower()
                
                show = search_text in prompt_text or search_text in response_text
                self.table.setRowHidden(row, not show)
    
    def view_result(self, result):
        """Показывает полный результат."""
        text = f"Дата: {result['saved_at']}\n"
        text += f"Промт: {result.get('prompt_text', '')}\n"
        text += f"Модель: {result.get('model_name', '')}\n"
        text += f"\nОтвет:\n{result['response']}"
        
        QMessageBox.information(self, "Результат", text)
    
    def delete_selected(self):
        """Удаляет выбранные результаты."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите результаты для удаления")
            return
        
        reply = QMessageBox.question(self, "Подтверждение",
                                   f"Удалить {len(selected_rows)} результат(ов)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            for row in selected_rows:
                prompt_item = self.table.item(row, 1)
                if prompt_item:
                    result_id = prompt_item.data(Qt.ItemDataRole.UserRole)
                    try:
                        db.delete_result(result_id)
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Не удалось удалить результат: {str(e)}")
            self.load_results()


class PromptImprovementThread(QThread):
    """Поток для асинхронного улучшения промта."""
    finished = pyqtSignal(dict)  # Сигнал с результатом улучшения
    error = pyqtSignal(str)  # Сигнал с ошибкой
    
    def __init__(self, original_prompt, model_id, improvement_type=None):
        super().__init__()
        self.original_prompt = original_prompt
        self.model_id = model_id
        self.improvement_type = improvement_type
    
    def run(self):
        """Выполняет улучшение промта в отдельном потоке."""
        try:
            result = prompt_improver.improve_prompt(
                self.original_prompt,
                self.model_id,
                self.improvement_type
            )
            self.finished.emit(result)
        except prompt_improver.PromptImprovementError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Неожиданная ошибка: {str(e)}")


class PromptImproverDialog(QDialog):
    """Диалог для улучшения промта с помощью AI-ассистента."""
    
    def __init__(self, parent=None, original_prompt=""):
        super().__init__(parent)
        self.original_prompt = original_prompt
        self.improvement_result = None  # Кэш последнего результата
        self.selected_prompt = None  # Выбранный промт для подстановки
        
        self.setWindowTitle("Улучшить промт")
        self.setGeometry(100, 100, 900, 700)
        self.init_ui()
        self.load_active_models()
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Выбор модели для улучшения
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Модель для улучшения:"))
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        
        # Выбор типа улучшения
        model_layout.addWidget(QLabel("Тип улучшения:"))
        self.improvement_type_combo = QComboBox()
        self.improvement_type_combo.addItem("Общее улучшение", None)
        self.improvement_type_combo.addItem("Для кода", "code")
        self.improvement_type_combo.addItem("Для анализа", "analysis")
        self.improvement_type_combo.addItem("Для креатива", "creative")
        model_layout.addWidget(self.improvement_type_combo)
        
        layout.addLayout(model_layout)
        
        # Исходный промт (read-only)
        original_group = QGroupBox("Исходный промт")
        original_layout = QVBoxLayout()
        self.original_text = QTextEdit()
        self.original_text.setPlainText(self.original_prompt)
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(100)
        original_layout.addWidget(self.original_text)
        original_group.setLayout(original_layout)
        layout.addWidget(original_group)
        
        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Вкладки с результатами
        self.tabs = QTabWidget()
        
        # Улучшенная версия
        self.improved_tab = QWidget()
        improved_layout = QVBoxLayout()
        self.improved_text = QTextEdit()
        self.improved_text.setPlaceholderText("Улучшенная версия промта появится здесь...")
        improved_layout.addWidget(self.improved_text)
        
        improved_buttons = QHBoxLayout()
        copy_improved_btn = QPushButton("Копировать")
        # Используем lambda для получения актуального текста из QTextEdit
        copy_improved_btn.clicked.connect(lambda checked, editor=self.improved_text: self.copy_to_clipboard(editor.toPlainText()))
        improved_buttons.addWidget(copy_improved_btn)
        
        use_improved_btn = QPushButton("Подставить в поле ввода")
        # Используем lambda для получения актуального текста из QTextEdit
        use_improved_btn.clicked.connect(lambda checked, editor=self.improved_text: self.use_prompt(editor.toPlainText()))
        improved_buttons.addWidget(use_improved_btn)
        improved_buttons.addStretch()
        
        improved_layout.addLayout(improved_buttons)
        self.improved_tab.setLayout(improved_layout)
        self.tabs.addTab(self.improved_tab, "Улучшенная версия")
        
        # Альтернативные варианты (будет добавлено динамически)
        self.alternative_tabs = []
        
        layout.addWidget(self.tabs)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.improve_btn = QPushButton("Улучшить промт")
        self.improve_btn.clicked.connect(self.start_improvement)
        self.improve_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        buttons_layout.addWidget(self.improve_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Отмена")
        close_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_active_models(self):
        """Загружает активные модели в выпадающий список."""
        try:
            active_models = models.ModelManager.get_active_models()
            self.model_combo.clear()
            
            if not active_models:
                QMessageBox.warning(
                    self,
                    "Предупреждение",
                    "Нет активных моделей. Добавьте хотя бы одну модель в настройках."
                )
                self.improve_btn.setEnabled(False)
                return
            
            for model in active_models:
                self.model_combo.addItem(model['name'], model['id'])
            
            self.improve_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модели: {str(e)}")
            self.improve_btn.setEnabled(False)
    
    def start_improvement(self):
        """Запускает процесс улучшения промта."""
        if not self.original_prompt or not self.original_prompt.strip():
            QMessageBox.warning(self, "Предупреждение", "Исходный промт не может быть пустым")
            return
        
        model_id = self.model_combo.currentData()
        if not model_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель для улучшения")
            return
        
        improvement_type = self.improvement_type_combo.currentData()
        
        # Проверяем кэш (если улучшаем тот же промт с теми же параметрами)
        cache_key = f"{self.original_prompt}_{model_id}_{improvement_type}"
        # Для простоты не используем кэш сейчас, но можно добавить позже
        
        # Блокируем UI
        self.improve_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        
        # Очищаем предыдущие результаты
        self.clear_results()
        
        # Создаем поток для асинхронной обработки
        self.improvement_thread = PromptImprovementThread(
            self.original_prompt,
            model_id,
            improvement_type
        )
        self.improvement_thread.finished.connect(self.on_improvement_finished)
        self.improvement_thread.error.connect(self.on_improvement_error)
        self.improvement_thread.start()
    
    def on_improvement_finished(self, result):
        """Обработчик завершения улучшения промта."""
        self.improve_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.improvement_result = result
        
        # Отображаем улучшенную версию
        improved_prompt = result.get('improved', '')
        self.improved_text.setPlainText(improved_prompt)
        
        # Отображаем альтернативные варианты
        alternatives = result.get('alternatives', [])
        for i, alt_prompt in enumerate(alternatives):
            if i >= 3:  # Максимум 3 альтернативы
                break
            
            # Создаем вкладку для альтернативы
            alt_tab = QWidget()
            alt_layout = QVBoxLayout()
            alt_text = QTextEdit()
            alt_text.setPlainText(alt_prompt)
            alt_text.setReadOnly(False)  # Позволяем редактировать
            alt_layout.addWidget(alt_text)
            
            alt_buttons = QHBoxLayout()
            copy_alt_btn = QPushButton("Копировать")
            # Используем lambda без захвата текста, чтобы всегда получать актуальный текст из QTextEdit
            copy_alt_btn.clicked.connect(lambda checked, editor=alt_text: self.copy_to_clipboard(editor.toPlainText()))
            alt_buttons.addWidget(copy_alt_btn)
            
            use_alt_btn = QPushButton("Подставить в поле ввода")
            # Используем lambda без захвата текста, чтобы всегда получать актуальный текст из QTextEdit
            use_alt_btn.clicked.connect(lambda checked, editor=alt_text: self.use_prompt(editor.toPlainText()))
            alt_buttons.addWidget(use_alt_btn)
            alt_buttons.addStretch()
            
            alt_layout.addLayout(alt_buttons)
            alt_tab.setLayout(alt_layout)
            
            tab_label = f"Альтернатива {i + 1}"
            self.tabs.addTab(alt_tab, tab_label)
            self.alternative_tabs.append((alt_tab, alt_text))
        
        QMessageBox.information(self, "Успех", "Промт успешно улучшен!")
    
    def on_improvement_error(self, error_message):
        """Обработчик ошибки при улучшении промта."""
        self.improve_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Ошибка", f"Не удалось улучшить промт:\n\n{error_message}")
    
    def clear_results(self):
        """Очищает результаты предыдущего улучшения."""
        self.improved_text.clear()
        # Удаляем вкладки с альтернативами (кроме первой вкладки с улучшенной версией)
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
        self.alternative_tabs.clear()
    
    def copy_to_clipboard(self, text):
        """
        Копирует текст в буфер обмена.
        
        Args:
            text: Текст для копирования. Если None или пустая строка, не копирует.
        """
        if not text or not text.strip():
            QMessageBox.warning(self, "Предупреждение", "Нет текста для копирования")
            return
        
        if PYQT_VERSION == 6:
            from PyQt6.QtWidgets import QApplication
        else:
            from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app:
            clipboard = app.clipboard()
            clipboard.setText(text)
            # Показываем краткое сообщение в статус-баре родительского окна, если доступно
            # Или просто информационное сообщение
            QMessageBox.information(self, "Успех", "Текст скопирован в буфер обмена")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить доступ к приложению")
    
    def use_prompt(self, text):
        """Подставляет промт в поле ввода главного окна."""
        self.selected_prompt = text
        self.accept()  # Закрываем диалог с кодом Accepted
    
    def get_selected_prompt(self):
        """Возвращает выбранный промт для подстановки."""
        return self.selected_prompt


class SettingsWindow(QDialog):
    """Окно настроек приложения."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Настройки приложения")
        self.setGeometry(100, 100, 500, 300)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Группа "Внешний вид"
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QVBoxLayout()
        appearance_group.setLayout(appearance_layout)
        
        # Выбор темы
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Тема интерфейса:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Светлая", "light")
        self.theme_combo.addItem("Тёмная", "dark")
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
        
        # Выбор размера шрифта
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Размер шрифта панелей:"))
        self.font_size_combo = QComboBox()
        # Добавляем варианты размеров шрифта (в пунктах)
        font_sizes = ["8", "9", "10", "11", "12", "13", "14", "16", "18", "20"]
        for size in font_sizes:
            self.font_size_combo.addItem(f"{size} pt", size)
        self.font_size_combo.currentIndexChanged.connect(self.on_font_size_changed)
        font_size_layout.addWidget(self.font_size_combo)
        font_size_layout.addStretch()
        appearance_layout.addLayout(font_size_layout)
        
        # Информация о применении настроек
        info_label = QLabel("Настройки применяются сразу после нажатия кнопки 'Применить' или 'ОК'")
        if PYQT_VERSION == 6:
            from PyQt6.QtGui import QFont
            info_font = QFont()
            info_font.setItalic(True)
            info_font.setPointSize(9)
            info_label.setFont(info_font)
            info_label.setStyleSheet("color: gray;")
        else:
            from PyQt5.QtGui import QFont
            info_font = QFont()
            info_font.setItalic(True)
            info_font.setPointSize(9)
            info_label.setFont(info_font)
            info_label.setStyleSheet("color: gray;")
        appearance_layout.addWidget(info_label)
        
        layout.addWidget(appearance_group)
        
        layout.addStretch()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Кнопка "Применить"
        self.apply_btn = QPushButton("Применить")
        self.apply_btn.clicked.connect(self.apply_settings)
        buttons_layout.addWidget(self.apply_btn)
        
        # Кнопка "ОК"
        ok_btn = QPushButton("ОК")
        ok_btn.clicked.connect(self.apply_and_close)
        ok_btn.setDefault(True)
        buttons_layout.addWidget(ok_btn)
        
        # Кнопка "Отмена"
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_settings(self):
        """Загружает настройки из БД."""
        try:
            # Загружаем тему
            theme = db.get_setting("theme")
            if theme:
                # Находим индекс темы
                for i in range(self.theme_combo.count()):
                    if self.theme_combo.itemData(i) == theme:
                        self.theme_combo.setCurrentIndex(i)
                        break
            else:
                # По умолчанию светлая тема
                self.theme_combo.setCurrentIndex(0)
            
            # Загружаем размер шрифта
            font_size = db.get_setting("font_size")
            if font_size:
                # Находим индекс размера шрифта
                for i in range(self.font_size_combo.count()):
                    if self.font_size_combo.itemData(i) == font_size:
                        self.font_size_combo.setCurrentIndex(i)
                        break
            else:
                # По умолчанию 10 pt
                default_font_size = "10"
                for i in range(self.font_size_combo.count()):
                    if self.font_size_combo.itemData(i) == default_font_size:
                        self.font_size_combo.setCurrentIndex(i)
                        break
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить настройки: {str(e)}")
    
    def on_theme_changed(self, index):
        """Обработчик изменения темы."""
        # Можно реализовать предпросмотр темы в будущем
        pass
    
    def on_font_size_changed(self, index):
        """Обработчик изменения размера шрифта."""
        # Можно реализовать предпросмотр размера шрифта в будущем
        pass
    
    def apply_settings(self):
        """Применяет настройки (сохраняет в БД и применяет к приложению)."""
        try:
            # Сохраняем тему
            theme = self.theme_combo.currentData()
            db.set_setting("theme", theme, "Тема интерфейса (light/dark)")
            
            # Сохраняем размер шрифта
            font_size = self.font_size_combo.currentData()
            db.set_setting("font_size", font_size, "Размер шрифта панелей в пунктах")
            
            # Применяем настройки к текущему окну
            if self.parent_window:
                self.parent_window.apply_theme(theme)
                self.parent_window.apply_font_size(int(font_size))
            
            QMessageBox.information(self, "Успех", "Настройки применены успешно!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить настройки: {str(e)}")
    
    def apply_and_close(self):
        """Применяет настройки и закрывает окно."""
        self.apply_settings()
        self.accept()
