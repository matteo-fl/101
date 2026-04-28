import requests

def generate_slides(data):
    prompt = data.get("prompt")

    # MOCK (замени на реальный API)
    return {
        "slides": [
            {
                "title": "Intro",
                "bullets": ["Point 1", "Point 2"]
            }
        ]
    }