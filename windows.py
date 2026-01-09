"""
Модуль с окнами управления для ChatList.
Содержит окна для управления промтами, моделями, результатами и настройками.
"""
import sys
from typing import Optional
import db
import models

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
        QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox,
        QMessageBox, QHeaderView, QGroupBox
    )
    from PyQt6.QtCore import Qt
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
        QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox,
        QMessageBox, QHeaderView, QGroupBox
    )
    from PyQt5.QtCore import Qt
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
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_models()
    
    def edit_model(self, model):
        """Редактирует модель."""
        dialog = EditModelDialog(self, model)
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("API URL:"))
        self.url_input = QLineEdit()
        if self.model:
            self.url_input.setText(self.model['api_url'])
        else:
            self.url_input.setPlaceholderText("https://api.openai.com/v1/chat/completions")
        layout.addWidget(self.url_input)
        
        layout.addWidget(QLabel("API ID (имя переменной окружения):"))
        self.api_id_input = QLineEdit()
        if self.model:
            self.api_id_input.setText(self.model['api_id'])
        else:
            self.api_id_input.setPlaceholderText("OPENAI_API_KEY")
        layout.addWidget(self.api_id_input)
        
        layout.addWidget(QLabel("Тип модели:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['openai', 'deepseek', 'groq', 'openrouter', 'unknown'])
        if self.model:
            model_type = self.model.get('model_type', 'unknown')
            index = self.type_combo.findText(model_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        layout.addWidget(self.type_combo)
        
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
