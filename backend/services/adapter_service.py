def to_canvas(llm_json):
    slides = []

    for slide in llm_json["slides"]:
        slides.append({
            "elements": [
                {
                    "type": "textbox",
                    "text": slide["title"],
                    "x": 100,
                    "y": 50
                },
                {
                    "type": "textbox",
                    "text": "\n".join(slide["bullets"]),
                    "x": 100,
                    "y": 150
                }
            ]
        })

    return {"slides": slides}