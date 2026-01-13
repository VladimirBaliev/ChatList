# Быстрый старт - Публикация на GitHub

## 🚀 Быстрая публикация релиза

### 1. Обновите версию
```bash
# Отредактируйте version.py
__version__ = "1.0.1"
```

### 2. Создайте тег и запушьте
```bash
git add version.py
git commit -m "Bump version to 1.0.1"
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin main
git push origin v1.0.1
```

### 3. GitHub Actions автоматически:
- ✅ Соберет приложение
- ✅ Создаст установщик (если доступен Inno Setup)
- ✅ Создаст GitHub Release с артефактами

## 📄 Обновление лендинга

1. Отредактируйте `docs/index.html`
2. Закоммитьте и запушьте:
```bash
git add docs/index.html
git commit -m "Update landing page"
git push origin main
```

GitHub Actions автоматически обновит GitHub Pages.

## ⚙️ Первоначальная настройка

1. **Настройте GitHub Pages**:
   - Settings → Pages → Source: `Deploy from a branch`
   - Branch: `main` → Folder: `/docs`

2. **Проверьте права**:
   - Settings → Actions → General
   - Workflow permissions: `Read and write permissions`

3. **Обновите ссылки в `docs/index.html`**:
   - Замените `VladimirBaliev` на ваш GitHub username
   - Или используйте переменные окружения GitHub

## 📚 Подробная инструкция

См. [GITHUB_RELEASE_GUIDE.md](GITHUB_RELEASE_GUIDE.md) для полной инструкции.
