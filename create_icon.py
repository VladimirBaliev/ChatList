from PIL import Image, ImageDraw, ImageFont
import os

def draw_icon(size):
    """Рисует светло-зелёный круг с буквами 'БВ'."""
    # Создаем RGB изображение с белым фоном (для лучшей видимости)
    img = Image.new("RGB", (size, size), (255, 255, 255))  # Белый фон
    draw = ImageDraw.Draw(img)
    
    # Вычисляем размеры с отступами (5% от размера с каждой стороны)
    padding = int(size * 0.05)
    circle_size = size - (padding * 2)
    
    # Координаты для круга (центрированный)
    center_x = size // 2
    center_y = size // 2
    radius = circle_size // 2
    
    # Рисуем светло-зелёный круг
    circle_coords = [
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius
    ]
    
    # Светло-зелёный цвет (LightGreen, примерно #90EE90)
    light_green = (144, 238, 144)
    draw.ellipse(circle_coords, fill=light_green)
    
    # Добавляем текст "БВ"
    text = "БВ"
    
    # Пытаемся загрузить системный шрифт с поддержкой кириллицы
    # Размер шрифта адаптируется к размеру иконки (для маленьких иконок уменьшаем)
    if size < 64:
        font_size = max(int(size * 0.6), 8)  # Для маленьких иконок - до 60%, минимум 8px
    else:
        font_size = int(size * 0.5)  # Для больших иконок - 50%
    
    font = None
    # Пробуем использовать системные шрифты Windows с поддержкой кириллицы
    # Сначала пробуем жирные версии для лучшей читаемости
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf",    # Segoe UI Bold - жирный современный шрифт
        "C:/Windows/Fonts/arialbd.ttf",     # Arial Bold - жирный классический шрифт
        "C:/Windows/Fonts/calibrib.ttf",    # Calibri Bold - жирный стандарт Office
        "C:/Windows/Fonts/tahomabd.ttf",    # Tahoma Bold - жирный с поддержкой кириллицы
        "C:/Windows/Fonts/segoeui.ttf",     # Segoe UI - обычный (если жирные не доступны)
        "C:/Windows/Fonts/arial.ttf",       # Arial - обычный
        "C:/Windows/Fonts/calibri.ttf",     # Calibri - обычный
        "C:/Windows/Fonts/tahoma.ttf",      # Tahoma - обычный
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        except Exception:
            continue
    
    if font is None:
        # Если не удалось загрузить системный шрифт, используем встроенный
        # (может не поддерживать кириллицу, но хотя бы попробуем)
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Рисуем текст только если шрифт доступен
    if font is not None:
        # Получаем размер текста для центрирования
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Вычисляем позицию для центрирования текста
            text_x = center_x - text_width // 2
            text_y = center_y - text_height // 2
            
            # Рисуем текст тёмным цветом для контраста
            # Используем почти чёрный цвет для лучшей читаемости на светло-зелёном фоне
            # Для маленьких иконок используем более тёмный цвет
            if size < 48:
                text_color = (0, 0, 0)  # Чёрный для маленьких иконок
            else:
                text_color = (0, 80, 0)  # Тёмно-зелёный для больших иконок
            
            draw.text((text_x, text_y), text, fill=text_color, font=font)
        except Exception as e:
            # Если не удалось нарисовать текст, просто оставляем круг
            print(f"   Предупреждение для размера {size}: не удалось добавить текст ({str(e)})")
    
    return img

# Размеры иконки
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = [draw_icon(s) for s, _ in sizes]

# Изображения уже в RGB режиме, просто убеждаемся
rgb_icons = []
for icon in icons:
    # Убеждаемся, что изображение в RGB режиме (не палитра)
    if icon.mode != "RGB":
        rgb_img = icon.convert("RGB")
    else:
        rgb_img = icon
    rgb_icons.append(rgb_img)

# Сохранение с явным указанием формата и цветов
# ВАЖНО: Изображения уже в RGB режиме, что гарантирует
# сохранение цветов и избегает автоматической конвертации в градации серого
try:
    rgb_icons[0].save(
        "app.ico",
        format="ICO",
        sizes=sizes,
        append_images=rgb_icons[1:]
    )
    print("✅ Иконка 'app.ico' создана!")
    print("   Дизайн: светло-зелёный круг с буквами 'БВ'")
    print("   Цвета: светло-зелёный фон круга, тёмно-зелёный текст")
except Exception as e:
    print(f"❌ Ошибка при сохранении: {e}")
    # Альтернативный способ - сохранить каждое изображение отдельно
    print("Попытка альтернативного метода сохранения...")
    rgb_icons[0].save("app.ico", format="ICO")
    print("✅ Иконка 'app.ico' создана (только один размер)")