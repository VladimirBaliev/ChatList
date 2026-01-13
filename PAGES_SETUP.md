# Настройка GitHub Pages

Если вы получили ошибку "Get Pages site failed", выполните следующие шаги:

## Вариант 1: Включение через веб-интерфейс (рекомендуется)

1. Перейдите на GitHub в ваш репозиторий: `https://github.com/VladimirBaliev/ChatList`
2. Откройте **Settings** (Настройки)
3. В левом меню выберите **Pages**
4. В разделе **Source** выберите:
   - **Source**: `Deploy from a branch`
   - **Branch**: `gh-pages` (или `main` с папкой `/docs`)
   - **Folder**: `/ (root)` или `/docs`
5. Нажмите **Save**

После этого workflow `.github/workflows/pages.yml` должен работать корректно.

## Вариант 2: Использование простого workflow

Если основной workflow не работает, можно использовать альтернативный:

1. Переименуйте `.github/workflows/pages-simple.yml` в `.github/workflows/pages.yml`
2. Или удалите старый `pages.yml` и используйте `pages-simple.yml`

Этот workflow создаст ветку `gh-pages` автоматически.

## Вариант 3: Ручное создание ветки gh-pages

```bash
# Создайте ветку gh-pages
git checkout --orphan gh-pages
git rm -rf .
cp -r docs/* .
git add -A
git commit -m "Initial GitHub Pages deployment"
git push origin gh-pages --force
git checkout main

# Затем в настройках GitHub выберите ветку gh-pages как источник
```

## Проверка

После настройки:
1. Подождите 1-2 минуты
2. Перейдите на `https://vladimirbaliev.github.io/ChatList/`
3. Если страница не открывается, проверьте настройки в Settings → Pages

