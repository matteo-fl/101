from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import os


class StyleTemplate:
    """Класс для хранения стилей оформления"""

    def __init__(self, name, colors, fonts, layout_params):
        self.name = name
        self.colors = colors
        self.fonts = fonts
        self.layout_params = layout_params


def get_style_template(style_name: str) -> StyleTemplate:
    """Возвращает шаблон стиля по названию"""
    styles = {
        "corporate": StyleTemplate(
            name="Корпоративный",
            colors={
                "primary": RGBColor(0x00, 0x52, 0xCC),  # Синий
                "secondary": RGBColor(0x6C, 0x75, 0x7D),  # Серый
                "accent": RGBColor(0x00, 0x9C, 0xDF),  # Светло-синий
                "text": RGBColor(0x33, 0x33, 0x33),  # Тёмно-серый
                "background": RGBColor(0xFF, 0xFF, 0xFF)  # Белый
            },
            fonts={
                "title": Pt(36),
                "subtitle": Pt(24),
                "body": Pt(18),
                "small": Pt(14)
            },
            layout_params={
                "title_y": Inches(0.6),
                "content_y": Inches(1.8),
                "image_x": Inches(8.5),
                "image_y": Inches(1.5),
                "image_width": Inches(4)
            }
        ),
        "creative": StyleTemplate(
            name="Креативный",
            colors={
                "primary": RGBColor(0xFF, 0x6B, 0x6B),  # Коралловый
                "secondary": RGBColor(0x4E, 0xC9, 0xCA),  # Бирюзовый
                "accent": RGBColor(0xFF, 0xE6, 0x6D),  # Жёлтый
                "text": RGBColor(0x2C, 0x3E, 0x50),  # Тёмно-синий
                "background": RGBColor(0xF9, 0xF9, 0xF9)  # Светло-серый
            },
            fonts={
                "title": Pt(40),
                "subtitle": Pt(28),
                "body": Pt(20),
                "small": Pt(16)
            },
            layout_params={
                "title_y": Inches(0.8),
                "content_y": Inches(2.0),
                "image_x": Inches(8.0),
                "image_y": Inches(1.2),
                "image_width": Inches(4.5)
            }
        ),
        "minimalist": StyleTemplate(
            name="Минималистичный",
            colors={
                "primary": RGBColor(0x00, 0x00, 0x00),  # Чёрный
                "secondary": RGBColor(0x80, 0x80, 0x80),  # Серый
                "accent": RGBColor(0xC0, 0xC0, 0xC0),  # Светло-серый
                "text": RGBColor(0x33, 0x33, 0x33),  # Тёмно-серый
                "background": RGBColor(0xFF, 0xFF, 0xFF)  # Белый
            },
            fonts={
                "title": Pt(32),
                "subtitle": Pt(22),
                "body": Pt(16),
                "small": Pt(12)
            },
            layout_params={
                "title_y": Inches(0.5),
                "content_y": Inches(1.5),
                "image_x": Inches(9.0),
                "image_y": Inches(1.8),
                "image_width": Inches(3.5)
            }
        )
    }
    return styles.get(style_name, styles["corporate"])


def add_title_slide(prs, slide_data: dict, style: StyleTemplate):
    """Добавляет титульный слайд"""
    layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(layout)

    # Настройка заголовка
    title = slide.shapes.title
    title.text = slide_data["title"]
    title.text_frame.paragraphs[0].font.size = style.fonts["title"]
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].font.color.rgb = style.colors["primary"]

    # Настройка подзаголовка
    if len(slide.placeholders) > 1:
        subtitle = slide.placeholders[1]
        subtitle.text = slide_data["content"]
        subtitle.text_frame.paragraphs[0].font.size = style.fonts["subtitle"]
        subtitle.text_frame.paragraphs[0].font.color.rgb = style.colors["secondary"]


def add_content_slide(prs, slide_data: dict, style: StyleTemplate, slide_num: int):
    """Добавляет контентный слайд"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)

    # Заголовок слайда
    title_box = slide.shapes.add_textbox(
        Inches(0.8),
        style.layout_params["title_y"],
        Inches(11),
        Inches(1)
    )
    title_frame = title_box.text_frame
    title_frame.paragraphs[0].text = slide_data["title"]
    title_frame.paragraphs[0].font.size = style.fonts["title"]
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = style.colors["primary"]

    # Контент слайда
    content_box = slide.shapes.add_textbox(
        Inches(0.8),
        style.layout_params["content_y"],
        Inches(7),
        Inches(5)
    )
    content_frame = content_box.text_frame
    content_frame.word_wrap = True

    # Разбиваем контент на абзацы
    paragraphs = slide_data["content"].split('\n')
    for i, para_text in enumerate(paragraphs):
        if i == 0:
            p = content_frame.paragraphs[0]
        else:
            p = content_frame.add_paragraph()

        p.text = para_text
        p.font.size = style.fonts["body"]
        p.font.color.rgb = style.colors["text"]
        p.space_after = Pt(12)

    # Добавляем визуальные элементы в зависимости от стиля
    if style.name == "Креативный":
        # Добавляем декоративную линию
        line = slide.shapes.add_shape(
            1,  # Линия
            Inches(0.8),
            style.layout_params["title_y"] + Inches(0.8),
            Inches(3),
            Inches(0.05)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = style.colors["accent"]

    # Вставка изображения (если есть)
    img_path = f"uploads/img_{slide_num}.png"
    if os.path.exists(img_path):
        try:
            slide.shapes.add_picture(
                img_path,
                style.layout_params["image_x"],
                style.layout_params["image_y"],
                width=style.layout_params["image_width"]
            )
        except Exception as e:
            print(f"⚠️ Пропуск битой картинки для слайда {slide_num + 1}: {e}")


def generate_presentation(slides_data: list, output_path: str, style_name: str = "corporate") -> str:
    """
    Генерация презентации с выбранным стилем

    Args:
        slides_data: список слайдов с полями title, content
        output_path: путь для сохранения
        style_name: стиль оформления (corporate, creative, minimalist)
    """
    # Устанавливаем размеры слайда
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Получаем шаблон стиля
    style = get_style_template(style_name)

    print(f"🎨 Генерация презентации в стиле: {style.name}")

    # Создаём слайды
    for i, slide in enumerate(slides_data):
        if i == 0:
            add_title_slide(prs, slide, style)
        else:
            add_content_slide(prs, slide, style, i)

    # Сохраняем презентацию
    prs.save(output_path)
    print(f"✅ Презентация сохранена: {output_path}")

    return output_path