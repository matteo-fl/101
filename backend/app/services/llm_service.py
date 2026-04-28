import os
import json
import uuid
from typing import Any
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("ROSTELECOM_API_TOKEN")
API_URL = "https://ai.rt.ru/api/1.0/llama/chat"


def generate_structure(
    prompt: str,
    doc_text: str,
    num_slides: int,
    style: str,
    tone: str
) -> list[Any] | None:
    """
    Генерация структуры презентации через LLM API Ростелекома.
    """

    # Добавляем документ как источник (если есть)
    if doc_text and len(doc_text) > 0:
        prompt_with_context = (
            f"Тема презентации: {prompt}\n\n"
            f"Используй этот документ как источник информации:\n{doc_text[:1500]}"
        )
    else:
        prompt_with_context = f"Тема презентации: {prompt}"

    system_prompt = (
        "Ты — профессиональный автор презентаций.\n"
        "Твоя задача — написать текст презентации в виде json структуры.\n\n"
        "ПРАВИЛА:\n"
        "1. Верни ТОЛЬКО валидный JSON-массив. Без markdown, без ```.\n"
        "2. Каждый слайд должен быть уникальным.\n"
        "3. Формат каждого слайда:\n"
        "   - title: заголовок (5–8 слов)\n"
        "   - content: 3–4 предложения раскрытия темы\n"
        "   - image_prompt: запрос для генерации изображения\n"
        "4. Строго следуй теме.\n"
        f"5. Создай ровно {num_slides} слайдов.\n"
        f"6. Тон повествования текста по теме: {tone}.\n"
    )

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "uuid": str(uuid.uuid4()),  # FIX: нужно вызвать функцию
        "chat": {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "user_message": prompt_with_context,
            "contents": [
                {
                    "type": "text",
                    "text": system_prompt,
                }
            ],
            "system_prompt": "Следуй инструкциям пользователя строго",
            "message_template": "<s>{role}\n{content}</s>",
            "response_template": "<s>bot\n",
            "max_new_tokens": 2000,
            "temperature": 0.4,
            "top_p": 0.9,
            "top_k": 40,
            "repetition_penalty": 1.1,
            "no_repeat_ngram_size": 15,
            "chat_history": []
        }
    }

    try:
        print("⚡ Отправка запроса к LLM...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
        response.raise_for_status()

        data = response.json()

        # Более безопасный парсинг ответа
        if isinstance(data, list):
            raw_text = data[0].get("message", {}).get("content", "")
        else:
            raw_text = data.get("message", {}).get("content", "")

        if not raw_text:
            raise ValueError("Пустой ответ от модели")

        # Очистка от markdown
        raw_text = (
            raw_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        structure = json.loads(raw_text)

        if not isinstance(structure, list):
            raise ValueError("LLM вернул не список")

        print(f"✅ Успешно сгенерировано {len(structure)} слайдов")

        return structure[:num_slides]

    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON парсинга: {e}")
        print(f"Ответ модели:\n{raw_text}")
        return None

    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return None