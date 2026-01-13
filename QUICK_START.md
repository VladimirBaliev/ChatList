# Быстрый старт - Публикация на GitHub

## 🚀 Быстрая публикация релиза

### 1. Обновите версию
```bash
# Отредактируйте version.py
__version__ = "1.0.0"
```

### 2. Создайте тег и релиз
```bash
git add version.py
git commit -m "Bump version to 1.0.0"
git push

git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 3. Создайте релиз на GitHub
1. Перейдите: **Releases** → **Draft a new release**
2. Выберите тег: `v1.0.0`
3. Заполните описание (используйте `RELEASE_NOTES_TEMPLATE.md`)
4. Нажмите **Publish release**

✅ GitHub Actions автоматически соберет и прикрепит файлы!

---

## 📄 Настройка GitHub Pages

### 1. Обновите ссылки в index.html
Замените `ваш-username` на ваш GitHub username:
- `https://github.com/ваш-username/ChatList` → ваша ссылка
- `https://github.com/ваш-username/ChatList/releases` → ваша ссылка

### 2. Включите GitHub Pages
1. **Settings** → **Pages**
2. **Source**: `GitHub Actions`
3. Сохраните

✅ Сайт будет доступен по адресу: `https://ваш-username.github.io/ChatList/`

---

## 📝 Подробная инструкция

См. [GITHUB_RELEASE_GUIDE.md](GITHUB_RELEASE_GUIDE.md) для полной инструкции.

