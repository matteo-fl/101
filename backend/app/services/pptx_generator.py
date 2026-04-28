from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import os

def generate_presentation(slides_data: list, output_path: str) -> str:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    PRIMARY = RGBColor(0x00, 0x52, 0xCC)
    TEXT = RGBColor(0x33, 0x33, 0x33)

    for i, slide in enumerate(slides_data):
        if i == 0:
            layout = prs.slide_layouts[0]
            s = prs.slides.add_slide(layout)
            s.shapes.title.text = slide["title"]
            s.placeholders[1].text = slide["content"]
        else:
            layout = prs.slide_layouts[5]
            s = prs.slides.add_slide(layout)
            tb = s.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11), Inches(1))
            p = tb.text_frame.paragraphs[0]
            p.font.size, p.font.bold, p.font.color.rgb = Pt(32), True, PRIMARY
            tb2 = s.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(7), Inches(5))
            p2 = tb2.text_frame.paragraphs[0]
            p2.text = slide["content"]
            p2.font.size, p2.font.color.rgb = Pt(20), TEXT
            tb2.text_frame.word_wrap = True
                        # Картинка (безопасная вставка)
            img_path = f"uploads/img_{i}.png"
            if os.path.exists(img_path):
                try:
                    s.shapes.add_picture(img_path, Inches(8.5), Inches(1.5), width=Inches(4))
                except Exception as e:
                    print(f"️ Пропуск битой картинки для слайда {i+1}: {e}")
    prs.save(output_path)
    return output_path
