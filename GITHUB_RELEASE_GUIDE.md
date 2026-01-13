# Пошаговая инструкция по публикации ChatList на GitHub Release и GitHub Pages

## Подготовка

### 1. Настройка репозитория

1. Убедитесь, что ваш репозиторий на GitHub настроен
2. Перейдите в **Settings** → **Actions** → **General**
3. В разделе **Workflow permissions** выберите **Read and write permissions**
4. Сохраните изменения

### 2. Настройка GitHub Pages

1. Перейдите в **Settings** → **Pages**
2. В разделе **Source** выберите:
   - **Source**: `Deploy from a branch`
   - **Branch**: `gh-pages` (или `main` с папкой `/docs`)
   - **Folder**: `/ (root)` или `/docs`
3. Сохраните изменения

## Автоматическая публикация (рекомендуется)

### Использование GitHub Actions

Проект настроен с автоматическими workflow:

1. **Автоматический релиз** (`.github/workflows/release.yml`):
   - Срабатывает при создании тега версии (например, `v1.0.0`)
   - Автоматически собирает приложение
   - Создает GitHub Release с артефактами

2. **Автоматический деплой на Pages** (`.github/workflows/pages.yml`):
   - Срабатывает при push в `main` или `gh-pages`
   - Обновляет лендинг на GitHub Pages

### Создание релиза (автоматически)

1. Обновите версию в `version.py`:
   ```python
   __version__ = "1.0.1"  # Новая версия
   ```

2. Создайте и запушьте тег:
   ```bash
   git add version.py
   git commit -m "Bump version to 1.0.1"
   git tag -a v1.0.1 -m "Release version 1.0.1"
   git push origin main
   git push origin v1.0.1
   ```

3. GitHub Actions автоматически:
   - Соберет приложение
   - Создаст Release с артефактами
   - Загрузит установщик и exe файлы

### Обновление лендинга

1. Отредактируйте `docs/index.html` (или `index.html` в корне)
2. Закоммитьте и запушьте:
   ```bash
   git add docs/index.html
   git commit -m "Update landing page"
   git push origin main
   ```

3. GitHub Actions автоматически обновит GitHub Pages

## Ручная публикация

### Создание релиза вручную

1. **Подготовка артефактов**:
   ```bash
   # Соберите приложение локально
   pyinstaller MinimalApp.spec
   
   # Создайте установщик (если используете Inno Setup)
   # Запустите generate_installer.py или скомпилируйте ChatList.iss
   ```

2. **Создание Release на GitHub**:
   - Перейдите в **Releases** → **Draft a new release**
   - Выберите или создайте тег (например, `v1.0.0`)
   - Заголовок: `ChatList v1.0.0`
   - Описание: используйте шаблон из `RELEASE_NOTES_TEMPLATE.md`
   - Загрузите артефакты:
     - `ChatList-Setup-v1.0.0.exe` (установщик)
     - `ChatList-v1.0.0.exe` (portable версия, опционально)
   - Отметьте **This is a pre-release** если это бета-версия
   - Нажмите **Publish release**

### Публикация на GitHub Pages вручную

1. **Создайте ветку gh-pages** (если еще нет):
   ```bash
   git checkout -b gh-pages
   git push origin gh-pages
   ```

2. **Скопируйте файлы лендинга**:
   ```bash
   # Скопируйте index.html в корень gh-pages или в docs/
   cp index.html docs/index.html
   ```

3. **Закоммитьте и запушьте**:
   ```bash
   git add docs/index.html
   git commit -m "Add landing page"
   git push origin gh-pages
   ```

4. GitHub автоматически опубликует страницу через несколько минут

## Структура файлов

```
ChatList/
├── .github/
│   └── workflows/
│       ├── release.yml          # Автоматический релиз
│       └── pages.yml            # Автоматический деплой на Pages
├── docs/
│   └── index.html               # Лендинг для GitHub Pages
├── version.py                   # Версия приложения
├── RELEASE_NOTES_TEMPLATE.md    # Шаблон для release notes
└── GITHUB_RELEASE_GUIDE.md      # Эта инструкция
```

## Проверка

### Проверка Release

1. Перейдите на страницу Releases: `https://github.com/ВАШ_USERNAME/ChatList/releases`
2. Убедитесь, что:
   - Release создан с правильной версией
   - Артефакты загружены и доступны для скачивания
   - Описание Release заполнено

### Проверка GitHub Pages

1. Перейдите на страницу: `https://ВАШ_USERNAME.github.io/ChatList/`
2. Убедитесь, что:
   - Лендинг отображается корректно
   - Все ссылки работают
   - Ссылки на скачивание ведут на правильные Release

## Обновление версии

При обновлении версии:

1. Обновите `version.py`
2. Обновите версию в `ChatList.iss` (если используете Inno Setup)
3. Обновите версию в `MinimalApp.spec` (если нужно)
4. Обновите ссылки на версию в `docs/index.html`
5. Создайте новый тег и релиз

## Troubleshooting

### GitHub Actions не запускаются

- Проверьте, что workflow файлы находятся в `.github/workflows/`
- Проверьте права доступа в Settings → Actions → General
- Проверьте логи в разделе Actions

### GitHub Pages не обновляется

- Убедитесь, что файлы находятся в правильной ветке/папке
- Проверьте настройки в Settings → Pages
- Подождите несколько минут (обновление может занять время)

### Артефакты не загружаются

- Проверьте размер файлов (лимит GitHub: 2GB на файл)
- Убедитесь, что файлы собраны корректно
- Проверьте логи GitHub Actions

## Дополнительные ресурсы

- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

