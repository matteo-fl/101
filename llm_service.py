import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

def generate_structure(prompt: str, doc_text: str, num_slides: int, style: str, tone: str) -> list:
    system_prompt = f"""
    Ты — эксперт по созданию бизнес-презентаций.
    На основе промпта и документа создай структуру ровно из {num_slides} слайдов.
    Верни ТОЛЬКО валидный JSON-массив без markdown-обёрток.
    Формат: [{{"title": "Заголовок", "content": "Основной текст (3-4 пункта)", "image_prompt": "Промпт на английском для картинки"}}, ...]
    Стиль: {style}. Тон: {tone}.
    """
    # 🔹 РАСКОММЕНТИРУЙТЕ ДЛЯ РЕАЛЬНОГО API
    """
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Промпт: {prompt}\n\nДокумент: {doc_text[:3000]}"}], "temperature": 0.7}
    resp = requests.post(LLM_API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()
    return json.loads(content)
    """
    # 🟡 MVP-ЗАГЛУШКА (работает без ключей)
    return [{"title": f"Слайд {i+1}: {prompt}", "content": f"Ключевые тезисы, адаптированные под стиль '{style}' и тон '{tone}'.", "image_prompt": f"Business illustration slide {i+1}, modern style"} for i in range(num_slides)]
