import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware # <--- ДОБАВИТЬ
import pypdf
from docx import Document
from dotenv import load_dotenv

from llm_service import generate_structure
from image_service import generate_image
from pptx_generator import create_pptx

load_dotenv()
app = FastAPI(title="AI PPTX Generator")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники (для локальной разработки/хакатона)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.makedirs("uploads", exist_ok=True)

# --- ДОБАВИТЬ CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], # Адреса React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate")
async def generate(
    prompt: str = Form(...),
    num_slides: int = Form(10),
    style: str = Form("Современный"),
    tone: str = Form("Профессиональный"),
    file: UploadFile = File(None)
):
    try:
        doc_text = ""
        if file and file.filename:
            # Логика чтения файла (как была раньше)
            path = os.path.join("uploads", file.filename)
            with open(path, "wb") as f: shutil.copyfileobj(file.file, f)
            if file.filename.lower().endswith(".pdf"):
                with open(path, "rb") as f: doc_text = "\n".join([p.extract_text() or "" for p in pypdf.PdfReader(f).pages])
            elif file.filename.lower().endswith(".docx"):
                doc = Document(path)
                doc_text = "\n".join([p.text for p in doc.paragraphs])

        structure = generate_structure(prompt, doc_text, num_slides, style, tone)

        # Генерация картинок
        for i, slide in enumerate(structure):
            if slide.get("image_prompt"):
                generate_image(slide["image_prompt"], f"uploads/img_{i}.png")

        create_pptx(structure, "uploads/result.pptx")
        return JSONResponse({"slides": structure, "message": "Готово!"})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download")
async def download():
    pptx_path = "uploads/result.pptx"
    if not os.path.exists(pptx_path):
        return JSONResponse({"error": "Файл не найден"}, status_code=404)
    return FileResponse(
        pptx_path,
        media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        filename='presentation.pptx'
    )