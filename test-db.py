#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовая программа для работы с SQLite базами данных.
Отображает список таблиц, позволяет просматривать данные с пагинацией
и выполнять CRUD операции.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from typing import Optional, List, Tuple
import os


class DatabaseViewer:
    """Главное окно приложения для просмотра и редактирования SQLite базы."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite Database Viewer")
        self.root.geometry("1000x700")
        
        self.db_path: Optional[str] = None
        self.connection: Optional[sqlite3.Connection] = None
        self.current_table: Optional[str] = None
        self.current_page = 1
        self.rows_per_page = 50
        
        self.setup_ui()
        
    def setup_ui(self):
        """Создание интерфейса приложения."""
        # Верхняя панель с выбором файла
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="База данных:").pack(side=tk.LEFT, padx=(0, 10))
        self.db_label = ttk.Label(top_frame, text="Не выбрана", foreground="gray")
        self.db_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(top_frame, text="Выбрать файл", command=self.select_database).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Закрыть", command=self.close_database).pack(side=tk.LEFT)
        
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель со списком таблиц
        left_frame = ttk.LabelFrame(main_container, text="Таблицы", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Список таблиц
        table_scrollbar = ttk.Scrollbar(left_frame)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.table_listbox = tk.Listbox(left_frame, width=25, height=20, yscrollcommand=table_scrollbar.set)
        self.table_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scrollbar.config(command=self.table_listbox.yview)
        
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # Кнопка "Открыть"
        ttk.Button(left_frame, text="Открыть", command=self.open_table).pack(pady=(10, 0), fill=tk.X)
        
        # Правая панель с данными таблицы
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Заголовок таблицы
        table_header = ttk.Frame(right_frame)
        table_header.pack(fill=tk.X, pady=(0, 10))
        
        self.table_title = ttk.Label(table_header, text="Выберите таблицу", font=("Arial", 12, "bold"))
        self.table_title.pack(side=tk.LEFT)
        
        # Кнопки CRUD
        crud_frame = ttk.Frame(table_header)
        crud_frame.pack(side=tk.RIGHT)
        
        ttk.Button(crud_frame, text="➕ Добавить", command=self.create_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="✏️ Редактировать", command=self.update_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="🗑️ Удалить", command=self.delete_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="🔄 Обновить", command=self.refresh_table).pack(side=tk.LEFT, padx=2)
        
        # Таблица данных с прокруткой
        table_container = ttk.Frame(right_frame)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Вертикальная прокрутка
        vsb = ttk.Scrollbar(table_container, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Горизонтальная прокрутка
        hsb = ttk.Scrollbar(table_container, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview для отображения данных
        self.tree = ttk.Treeview(table_container, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Пагинация
        pagination_frame = ttk.Frame(right_frame)
        pagination_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.page_info = ttk.Label(pagination_frame, text="")
        self.page_info.pack(side=tk.LEFT)
        
        pagination_buttons = ttk.Frame(pagination_frame)
        pagination_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(pagination_buttons, text="◀◀ Первая", command=lambda: self.change_page(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_buttons, text="◀ Предыдущая", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_buttons, text="Следующая ▶", command=self.next_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_buttons, text="Последняя ▶▶", command=self.goto_last_page).pack(side=tk.LEFT, padx=2)
        
    def select_database(self):
        """Выбор SQLite файла базы данных."""
        file_path = filedialog.askopenfilename(
            title="Выберите файл базы данных SQLite",
            filetypes=[("SQLite databases", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")]
        )
        
        if file_path:
            self.db_path = file_path
            self.db_label.config(text=Path(file_path).name, foreground="black")
            self.load_tables()
            
    def load_tables(self):
        """Загрузка списка таблиц из базы данных."""
        if not self.db_path:
            return
            
        try:
            if self.connection:
                self.connection.close()
                
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.table_listbox.delete(0, tk.END)
            for table in tables:
                self.table_listbox.insert(tk.END, table)
                
            if tables:
                self.table_listbox.selection_set(0)
                self.current_table = tables[0]
                
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить базу данных:\n{e}")
            
    def close_database(self):
        """Закрытие подключения к базе данных и очистка интерфейса."""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
            
        self.db_path = None
        self.current_table = None
        self.current_page = 1
        
        # Очистка списка таблиц
        self.table_listbox.delete(0, tk.END)
        
        # Очистка отображения данных
        self.tree.delete(*self.tree.get_children())
        self.tree['columns'] = []
        
        # Обновление меток
        self.db_label.config(text="Не выбрана", foreground="gray")
        self.table_title.config(text="Выберите таблицу")
        self.page_info.config(text="")
            
    def on_table_select(self, event):
        """Обработка выбора таблицы из списка."""
        selection = self.table_listbox.curselection()
        if selection:
            self.current_table = self.table_listbox.get(selection[0])
            
    def open_table(self):
        """Открытие выбранной таблицы."""
        if not self.current_table:
            messagebox.showwarning("Предупреждение", "Выберите таблицу из списка")
            return
            
        if not self.connection:
            messagebox.showerror("Ошибка", "База данных не подключена")
            return
            
        self.current_page = 1
        self.display_table()
        
    def get_table_columns(self) -> List[str]:
        """Получение списка столбцов таблицы."""
        if not self.current_table or not self.connection:
            return []
            
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = [row[1] for row in cursor.fetchall()]
        return columns
        
    def get_table_count(self) -> int:
        """Получение общего количества записей в таблице."""
        if not self.current_table or not self.connection:
            return 0
            
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.current_table}")
        return cursor.fetchone()[0]
        
    def display_table(self):
        """Отображение данных таблицы с пагинацией."""
        if not self.current_table or not self.connection:
            return
            
        try:
            # Очистка существующих данных
            self.tree.delete(*self.tree.get_children())
            
            # Получение столбцов
            columns = self.get_table_columns()
            if not columns:
                return
                
            # Настройка столбцов
            self.tree['columns'] = columns
            self.tree['show'] = 'headings'
            
            # Заголовки столбцов
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor=tk.W)
                
            # Подсчет общего количества записей
            total_rows = self.get_table_count()
            total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page if total_rows > 0 else 1
            
            # Обновление информации о странице
            self.page_info.config(
                text=f"Страница {self.current_page} из {total_pages} (Всего записей: {total_rows})"
            )
            
            # Загрузка данных с пагинацией
            offset = (self.current_page - 1) * self.rows_per_page
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {self.current_table} LIMIT ? OFFSET ?", 
                          (self.rows_per_page, offset))
            
            rows = cursor.fetchall()
            
            # Заполнение таблицы
            for row in rows:
                values = [str(val) if val is not None else "" for val in row]
                self.tree.insert("", tk.END, values=values)
                
            # Обновление заголовка
            self.table_title.config(text=f"Таблица: {self.current_table}")
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")
            
    def change_page(self, page: int):
        """Переход на указанную страницу."""
        if not self.current_table:
            return
            
        total_rows = self.get_table_count()
        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page if total_rows > 0 else 1
        
        if 1 <= page <= total_pages:
            self.current_page = page
            self.display_table()
            
    def prev_page(self):
        """Переход на предыдущую страницу."""
        if self.current_page > 1:
            self.change_page(self.current_page - 1)
            
    def next_page(self):
        """Переход на следующую страницу."""
        if not self.current_table:
            return
            
        total_rows = self.get_table_count()
        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page if total_rows > 0 else 1
        
        if self.current_page < total_pages:
            self.change_page(self.current_page + 1)
            
    def goto_last_page(self):
        """Переход на последнюю страницу."""
        if not self.current_table:
            return
            
        total_rows = self.get_table_count()
        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page if total_rows > 0 else 1
        
        if total_pages > 0:
            self.change_page(total_pages)
            
    def refresh_table(self):
        """Обновление отображения таблицы."""
        if self.current_table:
            self.display_table()
            
    def get_selected_row_data(self) -> Optional[List]:
        """Получение данных выбранной строки."""
        selection = self.tree.selection()
        if not selection:
            return None
            
        item = self.tree.item(selection[0])
        return item['values']
        
    def create_record(self):
        """Создание новой записи."""
        if not self.current_table or not self.connection:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
            
        columns = self.get_table_columns()
        if not columns:
            return
            
        # Открытие окна для ввода данных
        dialog = RecordDialog(self.root, "Добавить запись", columns)
        if dialog.result:
            try:
                values = dialog.result
                placeholders = ', '.join(['?' for _ in columns])
                columns_str = ', '.join(columns)
                
                cursor = self.connection.cursor()
                cursor.execute(f"INSERT INTO {self.current_table} ({columns_str}) VALUES ({placeholders})", values)
                self.connection.commit()
                
                messagebox.showinfo("Успех", "Запись успешно добавлена")
                self.refresh_table()
                
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить запись:\n{e}")
                self.connection.rollback()
                
    def update_record(self):
        """Редактирование выбранной записи."""
        if not self.current_table or not self.connection:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
            
        row_data = self.get_selected_row_data()
        if not row_data:
            messagebox.showwarning("Предупреждение", "Выберите строку для редактирования")
            return
            
        columns = self.get_table_columns()
        if not columns:
            return
            
        # Открытие окна для редактирования данных
        dialog = RecordDialog(self.root, "Редактировать запись", columns, row_data)
        if dialog.result:
            try:
                values = dialog.result
                
                # Получаем первичный ключ (первый столбец, предполагаем что это ID)
                # В реальном приложении лучше использовать PRAGMA table_info для определения PK
                primary_key_value = row_data[0] if row_data else None
                
                if primary_key_value is None:
                    messagebox.showerror("Ошибка", "Не удалось определить первичный ключ")
                    return
                    
                # Формируем SET часть UPDATE запроса
                set_clause = ', '.join([f"{col} = ?" for col in columns])
                
                cursor = self.connection.cursor()
                cursor.execute(f"UPDATE {self.current_table} SET {set_clause} WHERE {columns[0]} = ?", 
                             values + [primary_key_value])
                self.connection.commit()
                
                messagebox.showinfo("Успех", "Запись успешно обновлена")
                self.refresh_table()
                
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить запись:\n{e}")
                self.connection.rollback()
                
    def delete_record(self):
        """Удаление выбранной записи."""
        if not self.current_table or not self.connection:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
            
        row_data = self.get_selected_row_data()
        if not row_data:
            messagebox.showwarning("Предупреждение", "Выберите строку для удаления")
            return
            
        columns = self.get_table_columns()
        if not columns:
            return
            
        # Подтверждение удаления
        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Вы действительно хотите удалить эту запись?\n\n{columns[0]}: {row_data[0]}"
        )
        
        if not confirm:
            return
            
        try:
            primary_key_value = row_data[0]
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM {self.current_table} WHERE {columns[0]} = ?", [primary_key_value])
            self.connection.commit()
            
            messagebox.showinfo("Успех", "Запись успешно удалена")
            self.refresh_table()
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись:\n{e}")
            self.connection.rollback()


class RecordDialog:
    """Диалоговое окно для создания/редактирования записи."""
    
    def __init__(self, parent, title: str, columns: List[str], initial_values: Optional[List] = None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование окна
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.entries = {}
        
        # Контейнер с прокруткой
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Поля ввода для каждого столбца
        for i, column in enumerate(columns):
            ttk.Label(scrollable_frame, text=f"{column}:").grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            
            entry = ttk.Entry(scrollable_frame, width=40)
            if initial_values and i < len(initial_values):
                entry.insert(0, str(initial_values[i]) if initial_values[i] is not None else "")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.EW)
            
            self.entries[column] = entry
            
        scrollable_frame.columnconfigure(1, weight=1)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Отмена", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.RIGHT, padx=5)
        
        # Фокус на первое поле
        if columns:
            self.entries[columns[0]].focus()
            
        self.dialog.wait_window()
        
    def save(self):
        """Сохранение данных из формы."""
        self.result = [entry.get() for entry in self.entries.values()]
        self.dialog.destroy()
        
    def cancel(self):
        """Отмена диалога."""
        self.dialog.destroy()


def main():
    """Главная функция приложения."""
    root = tk.Tk()
    app = DatabaseViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()

