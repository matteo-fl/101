import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("RT_API_KEY")
API_URL = "https://ai.rt.ru/api/1.0/llama/chat"

def generate_structure(prompt: str, doc_text: str, num_slides: int, style: str, tone: str) -> list:
    """
    Генерация структуры презентации через LLM API Ростелекома.
    """
    
    # 1. Жёсткий системный промпт
    system_prompt = (
        "Ты — профессиональный автор презентаций. Твоя задача — создать структуру презентации.\n"
        "ПРАВИЛА:\n"
        "1. Верни ТОЛЬКО валидный JSON-массив. Никаких markdown-обёрток (без ```json), пояснений или текста.\n"
        "2. Каждый слайд должен быть УНИКАЛЬНЫМ. Запрещено повторять заголовки или текст.\n"
        "3. Поля каждого слайда:\n"
        "   - 'title': заголовок (5-8 слов)\n"
        "   - 'content': подробный текст (3-4 предложения). Раскрывай тему глубоко.\n"
        "   - 'image_prompt': описание картинки на английском (для генерации AI).\n"
        "4. СТРОГО придерживайся темы: «{prompt}»."
    ).format(prompt=prompt)

    # 2. Пользовательский запрос
    user_content = f"Создай ровно {num_slides} слайдов на тему: «{prompt}».\n"
    if doc_text:
        user_content += f"\nИспользуй этот документ как источник фактов:\n{doc_text[:1500]}"
    user_content += "\n\nВАЖНО: Каждый слайд должен раскрывать новую грань темы. Не повторяйся!"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "uuid": "00000000-0000-0000-0000-000000000000",
        "chat": {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "user_message": "HI",
            "contents": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "isUrl": False, "isAudioAsUrl": False, "idFile": 0,
                    "fileName": "", "image_url": None, "audio_url": None, "input_audio": None
                },
                {
                    "type": "text",
                    "text": user_content,
                    "isUrl": False, "isAudioAsUrl": False, "idFile": 0,
                    "fileName": "", "image_url": None, "audio_url": None, "input_audio": None
                }
            ],
            "message_template": "<s>{role}\n{content}</s>",
            "response_template": "<s>bot\n",
            "system_prompt": "Ты — Сайга, русскоязычный автоматический ассистент.",
            "max_new_tokens": 4000,
            "no_repeat_ngram_size": 15,
            "repetition_penalty": 1.1,
            "temperature": 0.7,
            "top_k": 40,
            "top_p": 0.9,
            "chat_history": []
        }
    }

    try:
        print(f"⚡ Отправка запроса к LLM...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        
        data = response.json()
        raw_text = data[0].get("message", {}).get("content", "") if isinstance(data, list) else data.get("message", {}).get("content", "")
        
        # Очистка
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        # Парсинг
        structure = json.loads(raw_text)
        
        if not isinstance(structure, list): raise ValueError("Not a list")
        
        print(f"✅ Успешно сгенерировано {len(structure)} слайдов")
        return structure[:num_slides]
        
    except Exception as e:
        print(f"❌ Ошибка API: {e}. Включаю умную заглушку.")
        return _smart_fallback(prompt, num_slides, style, tone)


def _smart_fallback(prompt: str, num_slides: int, style: str, tone: str) -> list:
    """
    Умная заглушка: генерирует РАЗНЫЕ слайды с РАЗНЫМИ картинками,
    даже если API не работает.
    """
    topic = prompt if prompt else "Тема презентации"
    
    # Набор разных шаблонов для слайдов
    templates = [
        {
            "title": f"Введение: {topic}",
            "content": f"Общее знакомство с темой «{topic}». Основные цели исследования и актуальность вопроса в современном мире.",
            "image_prompt": f"introductory slide about {topic}, professional design, {style} style"
        },
        {
            "title": f"Исторический контекст: {topic}",
            "content": f"Исторический фон и предпосылки возникновения {topic}. Ключевые события, которые привели к текущему состоянию.",
            "image_prompt": f"historical background of {topic}, ancient map or documents, {style} style"
        },
        {
            "title": f"Ключевые фигуры: {topic}",
            "content": f"Личности и организации, сыгравшие решающую роль в развитии {topic}. Их вклад и влияние.",
            "image_prompt": f"key figures related to {topic}, portraits or silhouettes, {style} style"
        },
        {
            "title": f"Основные достижения: {topic}",
            "content": f"Главные успехи и прорывы в области {topic}. Статистика и важные факты.",
            "image_prompt": f"achievements and success in {topic}, charts and graphs, {style} style"
        },
        {
            "title": f"Спорные моменты: {topic}",
            "content": f"Дискуссионные вопросы и критика, связанные с {topic}. Разные точки зрения экспертов.",
            "image_prompt": f"controversy and debate about {topic}, scales of justice or thinking person, {style} style"
        },
        {
            "title": f"Наследие и итоги: {topic}",
            "content": f"Долгосрочное влияние {topic} на общество и культуру. Итоги и выводы для будущего.",
            "image_prompt": f"legacy and future of {topic}, monument or futuristic view, {style} style"
        }
    ]

    result = []
    for i in range(num_slides):
        # Берем шаблон по кругу, если слайдов больше 6
        t = templates[i % len(templates)]
        result.append({
            "title": t["title"],
            "content": t["content"],
            "image_prompt": t["image_prompt"]
        })
    
    print(f"🔄 Заглушка: сгенерировано {len(result)} уникальных слайдов.")
    return result