import os
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
IMAGE_API_URL = os.getenv("IMAGE_API_URL", "")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY", "")

def generate_image(prompt: str, save_path: str) -> str | None:
    # 🔹 РАСКОММЕНТИРУЙТЕ ДЛЯ РЕАЛЬНОГО API (Kandinsky, DALL-E и др.)
    """
    headers = {"Authorization": f"Bearer {IMAGE_API_KEY}"}
    resp = requests.post(IMAGE_API_URL, headers=headers, json={"prompt": prompt})
    resp.raise_for_status()
    img_url = resp.json()["data"][0]["url"]
    with open(save_path, "wb") as f:
        f.write(requests.get(img_url).content)
    return save_path
    """

    # 🟡 НАДЁЖНАЯ MVP-ЗАГЛУШКА (генерирует картинку локально)
    try:
        img = Image.new('RGB', (1024, 768), color=(0, 82, 204))
        draw = ImageDraw.Draw(img)
        
        # Добавляем белый прямоугольник-подложку
        draw.rectangle([100, 200, 924, 568], fill=(255, 255, 255))
        
        # Текст по центру
        font = ImageFont.load_default(size=32)
        text = prompt[:40] + "..." if len(prompt) > 40 else prompt
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(((1024 - text_w) / 2, 350), text, fill=(0, 82, 204), font=font)
        
        img.save(save_path, "PNG")
        return save_path
    except Exception as e:
        print(f"⚠️ Ошибка генерации картинки: {e}")
        return None