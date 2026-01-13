# Настройка ссылок в index.html

Перед публикацией на GitHub Pages необходимо обновить все ссылки в файле `index.html`.

## Инструкция

1. Откройте файл `index.html`
2. Найдите все вхождения `ваш-username` (используйте Ctrl+F)
3. Замените на ваш реальный GitHub username

## Ссылки, которые нужно обновить:

### В разделе "Скачать ChatList":
- `https://github.com/ваш-username/ChatList/releases/latest`
- `https://github.com/ваш-username/ChatList`

### В разделе "Документация":
- `https://github.com/ваш-username/ChatList/blob/main/README.md`

### В футере:
- `https://github.com/ваш-username/ChatList`
- `https://github.com/ваш-username/ChatList/issues`
- `https://github.com/ваш-username/ChatList/releases`

## Пример

Если ваш GitHub username - `johndoe`, то:
- `https://github.com/ваш-username/ChatList` → `https://github.com/johndoe/ChatList`
- `https://github.com/ваш-username/ChatList/releases/latest` → `https://github.com/johndoe/ChatList/releases/latest`

## После настройки

1. Сохраните файл
2. Закоммитьте изменения:
   ```bash
   git add index.html
   git commit -m "Update links in landing page"
   git push
   ```
3. GitHub Actions автоматически обновит GitHub Pages
