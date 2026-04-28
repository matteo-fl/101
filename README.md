# 🚀 AI Генератор Презентаций (Ростелеком Хакатон)
## Быстрый старт
1. `python setup_project.py` (или просто распакуйте эту папку)
2. `cd ai-pptx-generator`
3. `python -m venv venv && source venv/bin/activate` (или `venv\Scripts\activate` на Windows)
4. `pip install -r requirements.txt`
5. `cp .env.example .env` и вставьте API-ключи
6. `uvicorn main:app --reload --port 8000`
7. Откройте: `http://localhost:8000`

## Структура
- `main.py` → FastAPI роуты
- `llm_service.py` → LLM API
- `image_service.py` → Генерация изображений
- `pptx_generator.py` → Сборка PPTX
- `templates/index.html` → Веб-интерфейс

## Для продакшена
- Раскомментируйте блоки `requests.post` в `llm_service.py` и `image_service.py`
- Замените заглушки на реальные API-эндпоинты
- Добавьте валидацию JSON через Pydantic
